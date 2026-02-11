import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.repositories.session_repository import save_message, get_last_messages, update_cart


@pytest.mark.asyncio
async def test_save_message_deduplicates():
    mock_sessions = SimpleNamespace(
        find_one=AsyncMock(return_value={"last_messages": [{"role": "user", "text": "Hi"}]}),
        update_one=AsyncMock()
    )
    mock_db = SimpleNamespace(sessions=mock_sessions)

    with patch("app.repositories.session_repository.get_database", return_value=mock_db):
        await save_message("s1", "user", "Hi")

    mock_sessions.update_one.assert_not_called()


@pytest.mark.asyncio
async def test_save_message_appends():
    mock_sessions = SimpleNamespace(
        find_one=AsyncMock(return_value={"last_messages": [{"role": "user", "text": "Hi"}]}),
        update_one=AsyncMock()
    )
    mock_db = SimpleNamespace(sessions=mock_sessions)

    with patch("app.repositories.session_repository.get_database", return_value=mock_db):
        await save_message("s1", "assistant", "Hello")

    mock_sessions.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_get_last_messages_empty():
    mock_sessions = SimpleNamespace(find_one=AsyncMock(return_value=None))
    mock_db = SimpleNamespace(sessions=mock_sessions)

    with patch("app.repositories.session_repository.get_database", return_value=mock_db):
        messages = await get_last_messages("s1")

    assert messages == []


@pytest.mark.asyncio
async def test_update_cart_persists():
    mock_sessions = SimpleNamespace(update_one=AsyncMock())
    mock_db = SimpleNamespace(sessions=mock_sessions)

    with patch("app.repositories.session_repository.get_database", return_value=mock_db):
        await update_cart("s1", [{"product_id": "p1", "quantity": 2}])

    mock_sessions.update_one.assert_called_once()
