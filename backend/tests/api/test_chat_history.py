import pytest


def test_chat_history_guest_requires_session_header(client):
    response = client.get("/chat/history")
    assert response.status_code == 400


def test_chat_history_guest_header_mismatch(client):
    response = client.get(
        "/chat/history",
        headers={"X-Session-Id": "s1"},
        params={"session_id": "s2"}
    )
    assert response.status_code == 400


def test_chat_history_guest_success(client, monkeypatch):
    async def fake_history(session_id, user_id, limit):
        return [{"role": "user", "text": "hi"}]

    monkeypatch.setattr("app.repositories.session_repository.get_chat_history", fake_history)

    response = client.get(
        "/chat/history",
        headers={"X-Session-Id": "s1"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["messages"][0]["text"] == "hi"


def test_chat_history_user_uses_token(client, monkeypatch):
    def fake_decode_token(token):
        return {"user_id": "u1"}

    async def fake_history(session_id, user_id, limit):
        return []

    monkeypatch.setattr("app.auth.decode_token", fake_decode_token)
    monkeypatch.setattr("app.repositories.session_repository.get_chat_history", fake_history)

    response = client.get(
        "/chat/history",
        headers={"Authorization": "Bearer token"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "user_u1"
