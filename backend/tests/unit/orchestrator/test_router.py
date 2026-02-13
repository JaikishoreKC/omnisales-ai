import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_route_request_sanitizes_unverified_action():
        with patch("app.orchestrator.router.detect_intent", return_value="cart"), \
            patch("app.orchestrator.router.build_context", new_callable=AsyncMock, return_value=""), \
            patch("app.orchestrator.router.generate_response", new_callable=AsyncMock, return_value="Order confirmed"), \
            patch("app.orchestrator.router.extract_product_name", return_value="Widget"), \
            patch("app.repositories.product_repository.find_product_by_name", new_callable=AsyncMock, return_value={"product_id": "p1", "name": "Widget", "price": 10, "stock": 5}), \
            patch("app.orchestrator.router.add_item", new_callable=AsyncMock, return_value=[]):

        from app.orchestrator.router import route_request
        result = await route_request("guest_s1", "s1", "add widget")

    assert "pending backend confirmation" in result["reply"].lower()


@pytest.mark.asyncio
async def test_route_request_allows_verified_action_reply():
        with patch("app.orchestrator.router.detect_intent", return_value="cart"), \
            patch("app.orchestrator.router.build_context", new_callable=AsyncMock, return_value=""), \
            patch("app.orchestrator.router.generate_response", new_callable=AsyncMock, return_value="Order confirmed"), \
            patch("app.orchestrator.router.extract_product_name", return_value="Widget"), \
            patch("app.repositories.product_repository.find_product_by_name", new_callable=AsyncMock, return_value={"product_id": "p1", "name": "Widget", "price": 10, "stock": 5}), \
            patch("app.orchestrator.router.add_item", new_callable=AsyncMock, return_value=[{"product_id": "p1"}]):

        from app.orchestrator.router import route_request
        result = await route_request("guest_s1", "s1", "add widget")

    assert result["reply"] == "Order confirmed"
