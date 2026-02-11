import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.repositories.order_repository import create_order, update_order_status


@pytest.mark.asyncio
async def test_create_order_sets_id():
    mock_orders = SimpleNamespace(insert_one=AsyncMock(return_value=SimpleNamespace(inserted_id="oid")))
    mock_db = SimpleNamespace(orders=mock_orders)

    with patch("app.repositories.order_repository.get_database", return_value=mock_db):
        order = await create_order("u1", [], 10.0, {"address": "x"})

    assert order["_id"] == "oid"


@pytest.mark.asyncio
async def test_update_order_status():
    mock_orders = SimpleNamespace(update_one=AsyncMock(return_value=SimpleNamespace(modified_count=1)))
    mock_db = SimpleNamespace(orders=mock_orders)

    with patch("app.repositories.order_repository.get_database", return_value=mock_db):
        ok = await update_order_status("o1", "shipped")

    assert ok is True
