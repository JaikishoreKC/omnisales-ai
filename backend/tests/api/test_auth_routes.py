import pytest


def test_register_success(client, monkeypatch):
    from app import auth as auth_module

    async def fake_get_user_by_email(email):
        return None

    async def fake_create_user(email, password, name):
        return {"user_id": "u1", "email": email, "name": name}

    def fake_create_access_token(data):
        return "token123"

    monkeypatch.setattr(auth_module, "get_user_by_email", fake_get_user_by_email)
    monkeypatch.setattr(auth_module, "create_user", fake_create_user)
    monkeypatch.setattr(auth_module, "create_access_token", fake_create_access_token)

    response = client.post(
        "/auth/register",
        json={"name": "Test", "email": "test@example.com", "password": "secret123"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["user"]["email"] == "test@example.com"
    assert data["token"] == "token123"


def test_login_success(client, monkeypatch):
    from app import auth as auth_module

    async def fake_get_user_by_email(email):
        return {"user_id": "u1", "email": email, "password_hash": "hash"}

    def fake_verify_password(plain, hashed):
        return True

    def fake_create_access_token(data):
        return "token123"

    monkeypatch.setattr(auth_module, "get_user_by_email", fake_get_user_by_email)
    monkeypatch.setattr(auth_module, "verify_password", fake_verify_password)
    monkeypatch.setattr(auth_module, "create_access_token", fake_create_access_token)

    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "secret123"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["user"]["email"] == "test@example.com"
    assert data["token"] == "token123"


def test_change_password_success(client, monkeypatch):
    from app import auth as auth_module

    def fake_decode_token(token):
        return {"user_id": "u1"}

    async def fake_change_password(user_id, old_password, new_password):
        return True

    monkeypatch.setattr(auth_module, "decode_token", fake_decode_token)
    monkeypatch.setattr(auth_module, "change_password", fake_change_password)

    response = client.post(
        "/auth/change-password",
        headers={"Authorization": "Bearer token123"},
        json={"old_password": "oldpass", "new_password": "newpass123"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Password changed" in data["message"]


def test_request_reset_token_dev_only(client, monkeypatch):
    from app import auth as auth_module

    async def fake_create_reset_token(email):
        return "reset-token"

    monkeypatch.setattr(auth_module, "create_reset_token", fake_create_reset_token)

    response = client.post(
        "/auth/request-reset",
        json={"email": "test@example.com"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "token" in data


def test_reset_password_success(client, monkeypatch):
    from app import auth as auth_module

    async def fake_reset_password_with_token(token, new_password):
        return True

    monkeypatch.setattr(auth_module, "reset_password_with_token", fake_reset_password_with_token)

    response = client.post(
        "/auth/reset-password",
        json={"token": "reset-token", "new_password": "newpass123"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Password reset" in data["message"]
