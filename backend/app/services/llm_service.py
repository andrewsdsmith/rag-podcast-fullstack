import asyncio
import logging
from collections.abc import AsyncGenerator

import openai

from app.api.deps import DbSession
from app.core.config import settings
from app.core.constants import CHUNK_DELIMITER
from app.models.server_sent_event import ServerSentEvent
from app.services import cache

logger = logging.getLogger(__name__)


async def stream_completion(
    system_prompt: str, user_prompt: str
) -> AsyncGenerator[tuple[str, str], None]:
    """Stream completion from OpenAI API.

    Returns: Chunks of the response while accumulating the full response.
    """
    try:
        response = openai.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            stream=True,
        )
    except Exception as e:
        logger.error(f"[LLM STREAMING ERROR] - {e}")
        raise

    full_response = ""

    for chunk in response:
        if chunk.choices[0].delta.content:
            chunk_content = chunk.choices[0].delta.content
            full_response += chunk_content + CHUNK_DELIMITER
            yield chunk_content, full_response


async def stream_llm_response(
    system_prompt: str,
    user_prompt: str,
    question: str,
    session: DbSession,
) -> AsyncGenerator[str, None]:
    """Stream LLM response with proper error handling."""
    response: str | None = None
    try:
        async for chunk, response in stream_completion(  # noqa: B007
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
