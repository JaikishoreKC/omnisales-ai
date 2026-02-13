import pytest


def test_cart_guest_requires_session_id(client):
    response = client.get("/cart")
    assert response.status_code == 400


def test_cart_guest_returns_items(client, monkeypatch):
    async def fake_get_cart(owner_type, owner_id):
        return [{"product_id": "p1", "price": 10, "quantity": 2}]

    monkeypatch.setattr("app.repositories.cart_repository.get_cart", fake_get_cart)

    response = client.get("/cart", headers={"X-Session-Id": "s1"})

    assert response.status_code == 200
    data = response.json()
    assert data["items"][0]["product_id"] == "p1"


def test_add_to_cart_rejects_out_of_stock(client, monkeypatch):
    async def fake_get_product_by_id(product_id):
        return {"product_id": product_id, "stock": 0}

    monkeypatch.setattr("app.repositories.product_repository.get_product_by_id", fake_get_product_by_id)

    response = client.post(
        "/cart/add",
        headers={"X-Session-Id": "s1"},
        json={"product_id": "p1", "quantity": 1}
    )

    assert response.status_code == 400


def test_add_to_cart_clamps_quantity_to_stock(client, monkeypatch):
    async def fake_get_product_by_id(product_id):
        return {"product_id": product_id, "name": "Widget", "price": 10, "stock": 2}

    async def fake_add_item(owner_type, owner_id, item):
        return [item]

    monkeypatch.setattr("app.repositories.product_repository.get_product_by_id", fake_get_product_by_id)
    monkeypatch.setattr("app.repositories.cart_repository.add_item", fake_add_item)

    response = client.post(
        "/cart/add",
        headers={"X-Session-Id": "s1"},
        json={"product_id": "p1", "quantity": 5}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["items"][0]["quantity"] == 2


def test_remove_cart_item_not_in_cart(client, monkeypatch):
    async def fake_get_product_by_id(product_id):
        return {"product_id": product_id, "name": "Widget", "price": 10, "stock": 2}

    async def fake_get_cart(owner_type, owner_id):
        return []

    monkeypatch.setattr("app.repositories.product_repository.get_product_by_id", fake_get_product_by_id)
    monkeypatch.setattr("app.repositories.cart_repository.get_cart", fake_get_cart)

    response = client.delete(
        "/cart/remove/p1",
        headers={"X-Session-Id": "s1"}
    )

    assert response.status_code == 404
