from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient
from sqlmodel import Session, select

from app.core.db import engine
from app.main import app
from app.models.podcast_segment_summary import PodcastSegmentSummary


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create a test client for making async requests."""
    client = AsyncClient(transport=ASGITransport(app), base_url="http://test")
    try:
        yield client
    finally:
        await client.aclose()


@pytest.fixture(scope="session")
def db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="session")
def check_db_populated(db: Session) -> Any:
    # Check if database has been populated with seed data
    result = db.exec(select(PodcastSegmentSummary)).first()
    assert result is not None, "Database should be populated with seed data"
    return result
