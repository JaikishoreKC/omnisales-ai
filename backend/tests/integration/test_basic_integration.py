import pytest
import httpx
from httpx import AsyncClient
from app.main import app
from app.orchestrator.intent import detect_intent


@pytest.mark.asyncio
async def test_health_endpoint(monkeypatch):
    from types import SimpleNamespace
    import app.core.database as db

    fake_db = SimpleNamespace(command=lambda *a, **k: {"ok": 1})

    async def fake_connect_db(*args, **kwargs):
        return None

    async def fake_close_db(*args, **kwargs):
        return None

    monkeypatch.setattr(db, "connect_db", fake_connect_db)
    monkeypatch.setattr(db, "close_db", fake_close_db)
    monkeypatch.setattr(db, "get_database", lambda: fake_db)

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_chat_endpoint(monkeypatch):
    async def fake_route_request(*args, **kwargs):
        return {"reply": "ok", "agent_used": "general", "actions": None}

    async def fake_save_message(*args, **kwargs):
        return None

    import app.orchestrator.router as router
    import app.repositories.session_repository as session_repo
    import app.core.database as db
    from types import SimpleNamespace

    monkeypatch.setattr(router, "route_request", fake_route_request)
    monkeypatch.setattr(session_repo, "save_message", fake_save_message)

    fake_db = SimpleNamespace(command=lambda *a, **k: {"ok": 1})

    async def fake_connect_db(*args, **kwargs):
        return None

    async def fake_close_db(*args, **kwargs):
        return None

    monkeypatch.setattr(db, "connect_db", fake_connect_db)
    monkeypatch.setattr(db, "close_db", fake_close_db)
    monkeypatch.setattr(db, "get_database", lambda: fake_db)

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/chat",
            headers={"Authorization": "Bearer test-api-key"},
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
