import pytest
from types import SimpleNamespace


def test_create_order_requires_auth(client):
    response = client.post(
        "/orders",
        json={
            "items": [{"product_id": "p1", "name": "Widget", "price": 10, "quantity": 1}],
            "total_amount": 10.8,
            "shipping_address": {
                "fullName": "Test",
                "email": "test@example.com",
                "phone": "123456",
                "address": "123 St",
                "city": "Town",
                "state": "ST",
                "zipCode": "12345",
                "country": "US"
            }
        }
    )
    assert response.status_code == 401


def test_create_order_total_mismatch(client, monkeypatch):
    def fake_decode_token(token):
        return {"user_id": "u1"}

    class FakeProducts:
        async def find_one(self, query):
            return {"product_id": "p1", "name": "Widget", "price": 10, "stock": 5}

        async def update_one(self, *args, **kwargs):
            return SimpleNamespace(modified_count=1)

    class FakeDb:
        products = FakeProducts()

    async def fake_create_order(user_id, items, total_amount, shipping_address):
        return {"order_id": "o1"}

    monkeypatch.setattr("app.auth.decode_token", fake_decode_token)
    monkeypatch.setattr("app.core.database.get_database", lambda: FakeDb())
    monkeypatch.setattr("app.main.get_database", lambda: FakeDb())
    monkeypatch.setattr("app.repositories.order_repository.create_order", fake_create_order)

    response = client.post(
        "/orders",
        headers={"Authorization": "Bearer token"},
        json={
            "items": [{"product_id": "p1", "name": "Widget", "price": 10, "quantity": 1}],
            "total_amount": 9.99,
            "shipping_address": {
                "fullName": "Test",
                "email": "test@example.com",
                "phone": "123456",
                "address": "123 St",
                "city": "Town",
                "state": "ST",
                "zipCode": "12345",
                "country": "US"
            }
        }
    )

    assert response.status_code == 400


def test_create_order_insufficient_stock(client, monkeypatch):
    def fake_decode_token(token):
        return {"user_id": "u1"}

    class FakeProducts:
        async def find_one(self, query):
            return {"product_id": "p1", "name": "Widget", "price": 10, "stock": 0}

    class FakeDb:
        products = FakeProducts()

    monkeypatch.setattr("app.auth.decode_token", fake_decode_token)
    monkeypatch.setattr("app.core.database.get_database", lambda: FakeDb())
    monkeypatch.setattr("app.main.get_database", lambda: FakeDb())

    response = client.post(
        "/orders",
        headers={"Authorization": "Bearer token"},
        json={
            "items": [{"product_id": "p1", "name": "Widget", "price": 10, "quantity": 1}],
            "total_amount": 10.8,
            "shipping_address": {
                "fullName": "Test",
                "email": "test@example.com",
                "phone": "123456",
                "address": "123 St",
                "city": "Town",
                "state": "ST",
                "zipCode": "12345",
                "country": "US"
            }
        }
    )

    assert response.status_code == 400
