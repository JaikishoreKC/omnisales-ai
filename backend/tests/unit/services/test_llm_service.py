import pytest

from app.services import llm_service


@pytest.mark.asyncio
async def test_routing_prefers_openrouter(monkeypatch):
    monkeypatch.setattr(llm_service, "OPENROUTER_API_KEY", "key")
    monkeypatch.setattr(llm_service, "OLLAMA_API_URL", "http://ollama")

    async def fake_openrouter(prompt):
        return "openrouter"

    async def fake_ollama(prompt):
        return "ollama"

    monkeypatch.setattr(llm_service, "_call_openrouter", fake_openrouter)
    monkeypatch.setattr(llm_service, "_call_ollama", fake_ollama)

    response = await llm_service.generate_response("hi")

    assert response == "openrouter"


@pytest.mark.asyncio
async def test_routing_falls_back_to_ollama(monkeypatch):
    monkeypatch.setattr(llm_service, "OPENROUTER_API_KEY", "")
    monkeypatch.setattr(llm_service, "OLLAMA_API_URL", "http://ollama")

    async def fake_ollama(prompt):
        return "ollama"

    monkeypatch.setattr(llm_service, "_call_ollama", fake_ollama)

    response = await llm_service.generate_response("hi")

    assert response == "ollama"


@pytest.mark.asyncio
async def test_routing_returns_fallback_when_no_provider(monkeypatch):
    monkeypatch.setattr(llm_service, "OPENROUTER_API_KEY", "")
    monkeypatch.setattr(llm_service, "OLLAMA_API_URL", "")

    response = await llm_service.generate_response("hi")

    assert "couldn't process" in response


@pytest.mark.asyncio
async def test_provider_error_is_handled(monkeypatch):
    monkeypatch.setattr(llm_service, "OPENROUTER_API_KEY", "key")
    monkeypatch.setattr(llm_service, "OLLAMA_API_URL", "http://ollama")

    async def failing_openrouter(prompt):
        raise RuntimeError("openrouter down")

    async def fake_ollama(prompt):
        return "ollama"

    monkeypatch.setattr(llm_service, "_call_openrouter", failing_openrouter)
    monkeypatch.setattr(llm_service, "_call_ollama", fake_ollama)

    response = await llm_service.generate_response("hi")

    assert response == "ollama"


@pytest.mark.asyncio
async def test_provider_returns_none_then_next(monkeypatch):
    monkeypatch.setattr(llm_service, "OPENROUTER_API_KEY", "key")
    monkeypatch.setattr(llm_service, "OLLAMA_API_URL", "http://ollama")

    async def none_openrouter(prompt):
        return None

    async def fake_ollama(prompt):
        return "ollama"

    monkeypatch.setattr(llm_service, "_call_openrouter", none_openrouter)
    monkeypatch.setattr(llm_service, "_call_ollama", fake_ollama)

    response = await llm_service.generate_response("hi")

    assert response == "ollama"
