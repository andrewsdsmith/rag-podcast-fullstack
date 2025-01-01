import logging
from collections.abc import AsyncGenerator

import openai

from app.core.config import settings
from app.core.constants import CHUNK_DELIMITER

logger = logging.getLogger(__name__)


async def stream_completion(
    system_prompt: str, user_prompt: str
) -> AsyncGenerator[tuple[str, str], None]:
    """Stream completion from OpenAI API."""
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
            content = chunk.choices[0].delta.content
            full_response += content + CHUNK_DELIMITER
            yield content, full_response
