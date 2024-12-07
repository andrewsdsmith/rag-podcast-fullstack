import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_db_connection(check_db_populated):
    """Test that database is properly populated with seed data."""
    segment = check_db_populated
    print(segment)
    assert segment.id is not None
    assert segment.title is not None
    assert segment.summary is not None
    assert segment.embedding is not None


async def test_generator_endpoint(client: AsyncClient):
    """Test the generator endpoint with a sample question."""
    client = await anext(client)  # Get the actual client from the async generator
    test_question = "What are the health benefits of intermittent fasting?"

    response = await client.post(
        "/api/v1/generator/question",
        json={"question": test_question},
        timeout=30.0,
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

    # Read and verify the streaming response
    content = []
    async for line in response.aiter_lines():
        if line.startswith("data: "):
            content.append(line[6:])  # Remove 'data: ' prefix
        if line == "data: [DONE]":
            break

    # Verify we received some content
    assert len(content) > 0
    # Optional: verify the first chunk is not empty
    assert len(content[0].strip()) > 0


async def test_generator_endpoint_empty_question(client: AsyncClient):
    """Test the generator endpoint with an empty question."""
    client = await anext(client)

    response = await client.post(
        "/api/v1/generator/question",
        json={"question": "   "},  # Empty question after stripping
        timeout=30.0,
    )

    assert response.status_code == 422  # Validation error


async def test_generator_endpoint_cached_response(client: AsyncClient):
    """Test the generator endpoint with a cached response."""
    client = await anext(client)
    test_question = "What are the health benefits of exercise?"

    # First request to cache the response
    response1 = await client.post(
        "/api/v1/generator/question",
        json={"question": test_question},
        timeout=30.0,
    )
    assert response1.status_code == 200

    # Collect content from first response
    content1 = []
    async for line in response1.aiter_lines():
        if line.startswith("data: "):
            data = line[6:]
            if data != "[DONE]":
                content1.append(data)

    # Second request should use cached response
    response2 = await client.post(
        "/api/v1/generator/question",
        json={"question": test_question},
        timeout=30.0,
    )

    assert response2.status_code == 200
    assert response2.headers["content-type"] == "text/event-stream; charset=utf-8"

    # Collect content from second response
    content2 = []
    async for line in response2.aiter_lines():
        if line.startswith("data: "):
            data = line[6:]
            if data != "[DONE]":
                content2.append(data)

    # Verify both responses are not empty
    assert len(content1) > 0
    assert len(content2) > 0

    # Join all content and compare the full text
    full_response1 = "".join(content1)
    full_response2 = "".join(content2)
    assert full_response1 == full_response2
