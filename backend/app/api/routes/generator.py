import asyncio
import logging
from collections.abc import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import TimeoutError

from app.api.deps import DbSession, PipelineBuilderDep
from app.core.constants import CHUNK_DELIMITER
from app.models.question_request import QuestionRequest
from app.models.server_sent_event import ServerSentEvent, ServerSentEventMessage
from app.services import cache, llm_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/question")
async def question_answer(
    request: QuestionRequest,
    pipeline_builder: PipelineBuilderDep,
    session: DbSession,
) -> StreamingResponse:
    try:
        user_question = request.question

        # Check cache
        cached_answer = await cache.get_cached_response(user_question, session)
        if cached_answer:

            async def stream_cached() -> AsyncGenerator[str, None]:
                try:
                    # Split by delimiter but filter out empty chunks
                    chunks = [c for c in cached_answer.text.split(CHUNK_DELIMITER) if c]
                    for chunk in chunks:
                        if chunk != "[DONE]":  # Don't wrap [DONE] in a message object
                            event = ServerSentEvent(
                                data=ServerSentEventMessage(message=chunk)
                            )
                            yield event.serialize()
                            await asyncio.sleep(0.005)

                    # Always send [DONE] in a consistent format
                    yield ServerSentEvent(
                        data=ServerSentEventMessage(message="[DONE]")
                    ).serialize()
                except Exception as e:
                    logger.error(f"Error streaming cached response: {e}", exc_info=True)
                    yield ServerSentEvent(
                        data=ServerSentEventMessage(
                            message="Error retrieving cached response"
                        )
                    ).serialize()

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
        """

        async def stream_response() -> AsyncGenerator[str, None]:
            try:
                async for (
                    content,
                    full_response,  # noqa: B007
                ) in llm_service.stream_completion(system_prompt, user_prompt):
                    yield ServerSentEvent(
                        data=ServerSentEventMessage(message=content)
                    ).serialize()
                    await asyncio.sleep(0)

                # Save final response
                await cache.save_response(user_question, full_response, session)
                yield ServerSentEvent(
                    data=ServerSentEventMessage(message="[DONE]")
                ).serialize()

            except Exception as e:
                logger.error(f"Error in stream generation: {e}", exc_info=True)
                yield ServerSentEvent(
                    data=ServerSentEventMessage(
                        message=f"Error generating response: {str(e)}"
                    )
                ).serialize()
                yield ServerSentEvent(
                    data=ServerSentEventMessage(message="[DONE]")
                ).serialize()

        return StreamingResponse(
            stream_response(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache"},
        )

    except TimeoutError:
        logger.error("Database connection timeout", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail="Database connection timeout. Please try again later.",
        )
    except Exception as e:
        logger.error(f"Error processing question: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error processing question")
