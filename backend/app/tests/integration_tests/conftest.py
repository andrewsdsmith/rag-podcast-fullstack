from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from sqlmodel import Session, select, delete

from app.core.db import engine
from app.main import app
from app.models.podcast_segment_summary import PodcastSegmentSummary
from app.models.question import Question
from app.models.answer import Answer


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create a test client for making async requests."""
    async with AsyncClient(
        transport=ASGITransport(app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture(scope="session")
def db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="session")
def check_db_populated(db: Session) -> Any:
    """
    Check if the database is populated with seed data before running tests.
    """
    result = db.exec(select(PodcastSegmentSummary)).first()
    assert result is not None, "Database should be populated with seed data"
    return result


@pytest.fixture(autouse=True)
def clear_tables(db: Session) -> None:
    """
    Clear both Question and Answer tables before each test.
    """
    # Clear questions first (due to foreign key to answers)
    # Valid sqlalchemy syntax but type hints are not included in the library
    db.exec(delete(Question))  # type: ignore[call-overload]

    db.exec(delete(Answer))  # type: ignore[call-overload]

    # Commit all changes
    db.commit()
