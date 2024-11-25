import logging
from collections.abc import AsyncGenerator

import openai

from app.core.config import settings

logger = logging.getLogger(__name__)


async def stream_completion(prompt_text: str) -> AsyncGenerator[tuple[str, str], None]:
    """Stream completion from OpenAI API."""
    try:
        response = openai.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "assistant", "content": prompt_text}],
            stream=True,
        )

        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response += content + "<!--CHUNK-->"
                yield content, full_response
    except Exception as e:
        logger.error(f"Error in OpenAI stream: {e}", exc_info=True)
        raise
