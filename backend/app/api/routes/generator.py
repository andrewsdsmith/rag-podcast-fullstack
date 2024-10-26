import asyncio
import logging
from collections.abc import AsyncGenerator, Generator
from contextlib import contextmanager

import openai
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import TimeoutError
from sqlmodel import select

from app.api.deps import PipelineBuilderDep, SessionDep
from app.models.answer import Answer
from app.models.question import Question

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@contextmanager
def session_scope(session: SessionDep) -> Generator[SessionDep, None, None]:
    """Provide a transactional scope around a series of operations."""
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


async def get_cached_response(text: str, session: SessionDep) -> Answer | None:
    """Check for cached response in the database."""
    try:
        # Use SQLModel's select syntax
        stmt = select(Question).where(Question.text == text)
        exact_matches = session.exec(stmt).all()

        if exact_matches:
            # Get the most recent match
            exact_match = max(exact_matches, key=lambda q: q.created_at)
            answer_stmt = select(Answer).where(Answer.id == exact_match.answer_id)
            return session.exec(answer_stmt).first()
    except Exception as e:
        logger.error(f"Error checking cache: {e}", exc_info=True)
    return None


async def save_response(text: str, answer_text: str, session: SessionDep) -> None:
    """Save the response to the database."""
    try:
        with session_scope(session):
            answer = Answer(text=answer_text)
            session.add(answer)
            session.flush()  # Flush to get the answer ID

            question_model = Question(text=text, answer_id=answer.id)
            session.add(question_model)
    except Exception as e:
        logger.error(f"Error saving response: {e}", exc_info=True)
        # Continue without failing - we don't want to interrupt the response stream
        # if saving fails


@router.get("/question")
async def question_answer(
    text: str, pipeline: PipelineBuilderDep, session: SessionDep
) -> StreamingResponse:
    try:
        text = text.strip()

        # Check cache first
        cached_answer = await get_cached_response(text, session)
        if cached_answer:

            async def db_response_generator() -> AsyncGenerator[str, None]:
                for char in cached_answer.text:
                    yield f"data: {char}\n\n"
                    await asyncio.sleep(0.01)
                yield "data: [DONE]\n\n"

            return StreamingResponse(
                db_response_generator(), media_type="text/event-stream"
            )

        # Process new question
        ra_pipeline = pipeline.build(session=session)
        augmented_prompt = ra_pipeline.run(
            {
                "embedder": {"text": text},
                "retriever": {"top_k": 15},
                "prompt": {"query": text},
            }
        )

        prompt_text = augmented_prompt["prompt"]["prompt"]
        logger.info(f"Generated prompt: {prompt_text[:200]}...")  # Log truncated prompt

        async def response_generator() -> AsyncGenerator[str, None]:
            full_response = ""
            try:
                response = openai.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "system", "content": prompt_text}],
                    stream=True,
                )

                for chunk in response:
                    if chunk.choices[0].delta.content is not None:
                        data = chunk.choices[0].delta.content
                        full_response += data
                        yield f"data: {data}\n\n"
                        await asyncio.sleep(0)

                yield "data: [DONE]\n\n"

                # Save response in background
                await save_response(text, full_response, session)

            except Exception as e:
                logger.error(f"Error in stream generation: {e}", exc_info=True)
                yield f"data: Error generating response: {str(e)}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(
            response_generator(),
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
