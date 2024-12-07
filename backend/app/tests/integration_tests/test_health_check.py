import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_health_check(client: AsyncClient):
    """Test health check endpoint returns OK status."""
    client = await anext(client)  # Get the actual client from the async generator
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
