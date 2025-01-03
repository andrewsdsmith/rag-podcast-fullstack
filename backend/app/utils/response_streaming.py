import asyncio
import logging
from collections.abc import AsyncGenerator

from app.core.constants import CHUNK_DELIMITER
from app.models.server_sent_event import ServerSentEvent

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
