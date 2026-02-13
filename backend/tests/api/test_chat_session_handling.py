import pytest
from app.auth import create_access_token


def test_chat_guest_requires_session_header(client, mock_chat_dependencies):
    response = client.post(
        "/chat",
        json={
            "user_id": "guest_s1",
            "session_id": "s1",
            "message": "hi",
            "channel": "web"
        }
    )

    assert response.status_code == 400


def test_chat_guest_header_match(client, mock_chat_dependencies):
    response = client.post(
        "/chat",
        headers={"X-Session-Id": "s1"},
        json={
            "user_id": "guest_s1",
            "session_id": "s1",
            "message": "hi",
            "channel": "web"
        }
    )

    assert response.status_code == 200


def test_chat_user_token_mismatch(client, mock_chat_dependencies):
    token = create_access_token({"user_id": "u1"})

    response = client.post(
        "/chat",
        headers={"X-User-Token": token},
        json={
            "user_id": "u2",
            "session_id": "s1",
            "message": "hi",
            "channel": "web"
        }
    )

    assert response.status_code == 401
