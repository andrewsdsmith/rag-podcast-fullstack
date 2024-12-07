import logging

from sqlmodel import select

from app.api.deps import DbSession
from app.models.answer import Answer
from app.models.question import Question

logger = logging.getLogger(__name__)


async def get_cached_response(text: str, session: DbSession) -> Answer | None:
    """Get cached response from the database."""
    try:
        stmt = select(Question).where(Question.text == text)
        exact_matches = session.exec(stmt).all()

        if exact_matches:
            exact_match = max(exact_matches, key=lambda q: q.created_at)
            answer_stmt = select(Answer).where(Answer.id == exact_match.answer_id)
            return session.exec(answer_stmt).first()

        return None
    except Exception as e:
        logger.error(f"Error checking cache: {e}", exc_info=True)
        return None


async def save_response(text: str, answer_text: str, session: DbSession) -> None:
    """Save response to the database."""
    try:
        answer = Answer(text=answer_text)
        session.add(answer)
        session.flush()

        question_model = Question(text=text, answer_id=answer.id)
        session.add(question_model)
        session.commit()
    except Exception as e:
        logger.error(f"Error saving response: {e}", exc_info=True)
        session.rollback()
