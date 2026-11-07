import pytest
import httpx
from app.core.config import settings
from app.jobs.ai_query import query_ai, query_ai_job


@pytest.mark.anyio
async def test_query_ai_mock_without_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "AI_API_KEY", "")
    response = await query_ai()
    assert "[MOCK AI]" in response


@pytest.mark.anyio
async def test_query_ai_with_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "AI_API_KEY", "test-key")
    monkeypatch.setattr(settings, "AI_API_URL", "https://api.openai.com/v1/chat/completions")
    monkeypatch.setattr(settings, "AI_MODEL", "gpt-4o-mini")

    async def mock_post(*args, **kwargs):
        class MockResponse:
            status_code = 200

            def raise_for_status(self):
                pass

            def json(self):
                return {
                    "choices": [
                        {"message": {"content": "Hello from AI!"}}
                    ]
                }
        return MockResponse()

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)
    response = await query_ai(prompt="Hello")
    assert response == "Hello from AI!"


@pytest.mark.anyio
async def test_query_ai_job_handles_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    async def mock_query_ai_failure(*args, **kwargs):
        raise RuntimeError("Network failure")

    monkeypatch.setattr("app.jobs.ai_query.query_ai", mock_query_ai_failure)
    # query_ai_job は例外をキャッチして安全に終了すること
    await query_ai_job()
