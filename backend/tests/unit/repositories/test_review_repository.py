import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from app.repositories.review_repository import create_review


@pytest.mark.asyncio
async def test_create_review_sets_id():
    mock_reviews = SimpleNamespace(insert_one=AsyncMock(return_value=SimpleNamespace(inserted_id="rid")))
    mock_db = SimpleNamespace(reviews=mock_reviews)

    with patch("app.repositories.review_repository.get_database", return_value=mock_db):
        review = await create_review("p1", "u1", "User", 5, "Great")

    assert review["_id"] == "rid"
