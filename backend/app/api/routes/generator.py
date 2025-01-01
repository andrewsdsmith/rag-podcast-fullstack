import asyncio
import logging
from collections.abc import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.api.deps import DbSession, PipelineBuilderDep
from app.core.constants import CHUNK_DELIMITER
from app.models.server_sent_event import ServerSentEvent
from app.services import cache, llm_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("")
async def question_answer(
    question: str,
    pipeline_builder: PipelineBuilderDep,
    session: DbSession,
) -> StreamingResponse:
    user_question = question.strip()
    # Validate input question
    if not user_question:
        return StreamingResponse(
            content="Invalid question",
            status_code=422,
            media_type="text/event-stream",
        )

    # Check cache
    cached_answer = await cache.get_cached_response(user_question, session)
    if cached_answer:

        async def stream_cached() -> AsyncGenerator[str, None]:
            # Split by delimiter but filter out empty chunks
            chunks = [c for c in cached_answer.text.split(CHUNK_DELIMITER) if c]
            for chunk in chunks:
                event = ServerSentEvent.from_message(message=chunk)
                yield event.serialize()
                await asyncio.sleep(0.005)

        return StreamingResponse(stream_cached(), media_type="text/event-stream")

    prompt_augmenter = pipeline_builder.build(session=session)
    # Generate augmented prompt
    pipeline_prompt_model = prompt_augmenter.run(
        {"embedder": {"text": user_question}, "retriever": {"top_k": 15}}
    )
    system_prompt = pipeline_prompt_model["prompt"]["prompt"]
    logger.info(f"Generated prompt: {system_prompt[:200]}...")

    user_prompt = f"""
        User Question:
        
        {user_question}
        """  # noqa: W293

    async def stream_response() -> AsyncGenerator[str, None]:
        full_response = None
        try:
            async for (
                content,
                full_response,  # noqa: B007
            ) in llm_service.stream_completion(system_prompt, user_prompt):
                yield ServerSentEvent.from_message(message=content).serialize()
                await asyncio.sleep(0)
        except Exception:
            yield ServerSentEvent.from_message(
                type="error",
                message="An error occured while trying to generate a response",
            ).serialize()
        else:
            # Save final response only if no exception was raised
            await cache.save_response(user_question, full_response, session)

    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )
