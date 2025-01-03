import logging

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from app.api.deps import DbSession, PipelineBuilderDep
from app.models.question_request import QuestionRequest
from app.services import cache, llm_service
from app.services.pipeline.pipeline_service import generate_pipeline_prompt
from app.utils import response_streaming

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("")
async def question_answer(
    question: str,
    pipeline_builder: PipelineBuilderDep,
    session: DbSession,
) -> StreamingResponse:
    """
    Stream an LLM generated answer to a question, using cache if available.
    The LLM prompt is augmented with Zoe podcast transcript data.
    """
    try:
        # Validate question using pydantic
        validated_question = QuestionRequest(question=question).question
    except Exception:
        logger.exception("Invalid question format")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid question format",
        )

    try:
        # Check cache first
        cached_answer = await cache.get_cached_response(validated_question, session)
        if cached_answer:
            return StreamingResponse(
                response_streaming.stream_cached_response(cached_answer.text),
                media_type="text/event-stream",
            )

        # Generate prompt if no cache hit
        system_prompt = await generate_pipeline_prompt(
            validated_question, pipeline_builder, session
        )
        user_prompt = f"""
            User Question:
            
            {validated_question}
            """  # noqa: W293

        return StreamingResponse(
            llm_service.stream_llm_response(
                system_prompt, user_prompt, validated_question, session
            ),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache"},
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error in question_answer endpoint")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
