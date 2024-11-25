import asyncio
import logging
from collections.abc import AsyncGenerator

import openai
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import TimeoutError

from app.api.deps import PipelineBuilderDep, SessionDep
from app.models.sse_event import SSEEvent, SSEEventMessage
from app.services import cache

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/question")
async def question_answer(
    text: str, pipeline: PipelineBuilderDep, session: SessionDep
) -> StreamingResponse:
    try:
        text = text.strip()

        # Check cache
        cached_answer = await cache.get_cached_response(text, session)
        if cached_answer:

            async def stream_cached() -> AsyncGenerator[str, None]:
                for chunk in cached_answer.text.split("<!--CHUNK-->"):
                    event = SSEEvent(data=SSEEventMessage(message=chunk))
                    yield event.serialize()
                    await asyncio.sleep(0.005)
                yield SSEEvent(data=SSEEventMessage(message="[DONE]")).serialize()

            return StreamingResponse(stream_cached(), media_type="text/event-stream")

        # Generate augmented prompt
        ra_pipeline = pipeline.build(session=session)
        augmented_prompt = ra_pipeline.run(
            {
                "embedder": {"text": text},
                "retriever": {"top_k": 15},
                "prompt": {"query": text},
            }
        )
        prompt_text = augmented_prompt["prompt"]["prompt"]
        logger.info(f"Generated prompt: {prompt_text[:200]}...")

        async def stream_response() -> AsyncGenerator[str, None]:
            try:
                async for (
                    content,
                    full_response,  # noqa: B007
                ) in openai.stream_completion(prompt_text):
                    yield SSEEvent(data=SSEEventMessage(message=content)).serialize()
                    await asyncio.sleep(0)

                # Save final response
                await cache.save_response(text, full_response, session)
                yield SSEEvent(data=SSEEventMessage(message="[DONE]")).serialize()

            except Exception as e:
                logger.error(f"Error in stream generation: {e}", exc_info=True)
                yield f"data: Error generating response: {str(e)}\n\n"
                yield "data: [DONE]\n\n"

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
