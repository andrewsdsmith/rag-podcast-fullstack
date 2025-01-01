import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

GENERATOR_ENDPOINT = "/api/v1/generator"


def generate_endpoint_from_question(question: str) -> str:
    return f"{GENERATOR_ENDPOINT}?question={question}"


async def test_generator_endpoint(client: AsyncClient) -> None:
    """Test the generator endpoint."""
    test_question = "What are the health benefits of exercise?"

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

    for line1, line2 in zip(lines1, lines2):
        assert line1 == line2
        assert "event: error" not in line1
        assert "event: error" not in line2


# TODO: Fix this test - mocking openai.chat.completions.create is not working
# async def test_llm_service_exception(client: AsyncClient) -> None:
#     """Test handling of LLM service exceptions."""
#     test_question = "What are the health benefits of exercise?"

#     def test_mock_works():
#         print("Mock works")
#         raise Exception("An error occured while trying to generate a response")

#     # Mock the LLM service to raise an exception
#     with patch(
#         "app.api.routes.generator.llm_service.stream_completion",
#         new_callable=AsyncMock,
#         side_effect=test_mock_works,
#     ):
#         response = await client.get(
#             generate_endpoint_from_question(test_question),
#             timeout=30.0,
#         )

#         lines = [line async for line in response.aiter_lines()]
#         assert any("event: error" in line for line in lines)
#         assert any(
#             "An error occured while trying to generate a response" in line
#             for line in lines
#         )
