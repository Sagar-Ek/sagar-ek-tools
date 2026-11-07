from unittest.mock import MagicMock
import pytest
from app.jobs.ai_query import normalize_model_name, query_ai, query_ai_job


def test_normalize_model_name() -> None:
    assert normalize_model_name("gemini-3.1-flash-lite") == "gemini/gemini-3.1-flash-lite"
    assert normalize_model_name("gemini/gemini-3.1-flash-lite") == "gemini/gemini-3.1-flash-lite"
    assert normalize_model_name("gpt-4o-mini") == "gpt-4o-mini"


@pytest.mark.anyio
async def test_query_ai_mock_without_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AI_API_KEY", raising=False)
    response = await query_ai()
    assert "[MOCK AI]" in response


@pytest.mark.anyio
async def test_query_ai_with_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AI_API_KEY", "test-key")
    monkeypatch.setenv("AI_MODEL", "gemini/gemini-3.1-flash-lite")

    async def mock_acompletion(*args, **kwargs):
        mock_choice = MagicMock()
        mock_choice.message.content = "Hello from LiteLLM!"
        mock_resp = MagicMock()
        mock_resp.choices = [mock_choice]
        return mock_resp

    monkeypatch.setattr("app.jobs.ai_query.acompletion", mock_acompletion)
    response = await query_ai(prompt="Hello")
    assert response == "Hello from LiteLLM!"


@pytest.mark.anyio
async def test_query_ai_job_handles_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    async def mock_query_ai_failure(*args, **kwargs):
        raise RuntimeError("LiteLLM connection error")

    monkeypatch.setattr("app.jobs.ai_query.query_ai", mock_query_ai_failure)
    await query_ai_job()
