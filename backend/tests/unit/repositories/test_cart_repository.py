import pytest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.repositories.cart_repository import add_item, remove_item, update_quantity, get_cart


class FakeCarts:
    def __init__(self, initial=None):
        self._items = initial or []
        self.update_one = AsyncMock()

    async def find_one(self, query):
        if self._items:
            return {"items": list(self._items)}
        return None


@pytest.mark.asyncio
async def test_add_item_creates_new_entry():
    carts = FakeCarts()
    db = SimpleNamespace(carts=carts)

    with patch("app.repositories.cart_repository.get_database", return_value=db):
        items = await add_item("guest", "s1", {"product_id": "p1", "quantity": 1})

    assert len(items) == 1
    assert items[0]["product_id"] == "p1"
    assert items[0]["quantity"] == 1
    carts.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_add_item_increments_quantity():
    carts = FakeCarts(initial=[{"product_id": "p1", "quantity": 1}])
    db = SimpleNamespace(carts=carts)

    with patch("app.repositories.cart_repository.get_database", return_value=db):
        items = await add_item("guest", "s1", {"product_id": "p1", "quantity": 2})

    assert len(items) == 1
    assert items[0]["quantity"] == 3
    carts.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_update_quantity_removes_when_zero():
    carts = FakeCarts(initial=[{"product_id": "p1", "quantity": 2}])
    db = SimpleNamespace(carts=carts)

    with patch("app.repositories.cart_repository.get_database", return_value=db):
        items = await update_quantity("guest", "s1", "p1", 0)

    assert items == []
    carts.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_remove_item_filters_product():
    carts = FakeCarts(initial=[{"product_id": "p1", "quantity": 1}, {"product_id": "p2", "quantity": 1}])
    db = SimpleNamespace(carts=carts)

    with patch("app.repositories.cart_repository.get_database", return_value=db):
        items = await remove_item("guest", "s1", "p1")

    assert len(items) == 1
    assert items[0]["product_id"] == "p2"
    carts.update_one.assert_called_once()
