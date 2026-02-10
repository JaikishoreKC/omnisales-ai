import pytest
import httpx
from httpx import AsyncClient
from app.main import app
from app.orchestrator.intent import detect_intent


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_chat_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/chat",
            json={
                "user_id": "test_user",
                "session_id": "test_session",
                "message": "hello"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
        assert "agent_used" in data


def test_intent_detection():
    assert detect_intent("recommend me a laptop") == "recommendation"
    assert detect_intent("is this available?") == "inventory"
    assert detect_intent("I want to buy") == "payment"
    assert detect_intent("track my order") == "tracking"
    assert detect_intent("hello") == "general"
