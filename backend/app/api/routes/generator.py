import asyncio
import logging
from collections.abc import AsyncGenerator
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from app.api.deps import DbSession, PipelineBuilderDep
from app.core.constants import CHUNK_DELIMITER
from app.models.server_sent_event import ServerSentEvent
from app.services import cache, llm_service
from app.models.question_request import QuestionRequest

router = APIRouter()
logger = logging.getLogger(__name__)


async def stream_cached_response(response: str) -> AsyncGenerator[str, None]:
    """Stream a cached response with proper error handling."""
    try:
        chunks = [c for c in response.split(CHUNK_DELIMITER) if c]
        for chunk in chunks:
            yield ServerSentEvent.from_message(message=chunk).serialize()
            await asyncio.sleep(0.005)
        yield ServerSentEvent(type="message", message="[DONE]").serialize()
    except Exception:
        logger.exception("Error streaming cached response")
        yield ServerSentEvent.from_message(
            type="error",
            message="Error retrieving cached response",
        ).serialize()


async def generate_pipeline_prompt(
    question: str,
    pipeline_builder: PipelineBuilderDep,
    session: DbSession,
) -> str:
    """Generate and validate the pipeline prompt."""
    try:
        prompt_augmenter = pipeline_builder.build(session=session)
        pipeline_prompt_model = prompt_augmenter.run(
            {"embedder": {"text": question}, "retriever": {"top_k": 15}}
        )
        prompt = pipeline_prompt_model["prompt"]["prompt"]
        logger.info(f"Generated prompt: {prompt[:200]}...")
        return prompt
    except Exception:
        logger.exception("Failed to generate pipeline prompt")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process question",
        )


async def stream_llm_response(
    system_prompt: str,
    user_prompt: str,
    question: str,
    session: DbSession,
) -> AsyncGenerator[str, None]:
    """Stream LLM response with proper error handling."""
    response: Optional[str] = None
    try:
        async for chunk, response in llm_service.stream_completion(
            system_prompt, user_prompt
        ):
            yield ServerSentEvent.from_message(message=chunk).serialize()
            await asyncio.sleep(0)
        yield ServerSentEvent(type="message", message="[DONE]").serialize()
    except Exception:
        logger.exception("LLM streaming failed")
        yield ServerSentEvent.from_message(
            type="error",
            message="Failed to generate response. Please try again later.",
        ).serialize()
    else:
        if response:  # Cache only successful responses
            try:
                await cache.save_response(question, response, session)
            except Exception:
                logger.exception("Failed to cache response")


@router.get("")
async def question_answer(
    question: str,
    pipeline_builder: PipelineBuilderDep,
    session: DbSession,
) -> StreamingResponse:
    """
    Stream an answer to a question, using cache if available.
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
                stream_cached_response(cached_answer.text),
                media_type="text/event-stream",
            )

        # Generate prompt if no cache hit
        system_prompt = await generate_pipeline_prompt(
            validated_question, pipeline_builder, session
        )
        user_prompt = f"""
            User Question:
            
            {validated_question}
            """

        return StreamingResponse(
            stream_llm_response(
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
