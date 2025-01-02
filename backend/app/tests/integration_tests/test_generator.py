import pytest
from httpx import AsyncClient
from unittest.mock import patch

pytestmark = pytest.mark.asyncio

GENERATOR_ENDPOINT = "/api/v1/generator"


def generate_endpoint_from_question(question: str) -> str:
    return f"{GENERATOR_ENDPOINT}?question={question}"


# TODO: clear database before running tests
async def test_generator_endpoint(client: AsyncClient) -> None:
    """Test the generator endpoint."""
    test_question = "Is intermittent fasting healthy?"

    response = await client.get(
        generate_endpoint_from_question(test_question),
        timeout=30.0,
    )

    lines = [line async for line in response.aiter_lines()]

    assert lines
    assert "event: error" not in lines[0]


async def test_generator_endpoint_empty_question(client: AsyncClient) -> None:
    """Test the generator endpoint with an empty question."""
    response = await client.get(
        generate_endpoint_from_question(""),
        timeout=30.0,
    )

    assert response.status_code == 422


async def test_generator_endpoint_cached_response(client: AsyncClient) -> None:
    """Test the generator endpoint with a cached response."""
    test_question = "What are the health benefits of exercise?"

    # First request to cache the response
    response1 = await client.get(
        generate_endpoint_from_question(test_question),
        timeout=30.0,
    )

    # Second request should use cached response
    response2 = await client.get(
        generate_endpoint_from_question(test_question),
        timeout=30.0,
    )

    lines1 = [line async for line in response1.aiter_lines()]
    lines2 = [line async for line in response2.aiter_lines()]

    assert len(lines1) == len(lines2)

    for line1, line2 in zip(lines1, lines2, strict=False):
        assert line1 == line2
        assert "event: error" not in line1
        assert "event: error" not in line2


async def test_generator_endpoint_llm_service_exception(client: AsyncClient) -> None:
    """Test the generator endpoint handles exceptions from llm_service correctly."""
    test_question = "What is the capital of France?"

    with patch("app.services.llm_service.stream_completion") as mock_stream_completion:
        mock_stream_completion.side_effect = Exception("Test exception")

        response = await client.get(
            generate_endpoint_from_question(test_question),
            timeout=30.0,
        )

        lines = [line async for line in response.aiter_lines()]
        print("lines", lines)
        assert lines
        assert "event: error" in lines[0]
        assert "An error occured while trying to generate a response" in lines[1]
