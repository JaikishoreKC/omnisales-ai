"""
Shared test fixtures and configuration
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def api_key():
    """Valid API key for testing"""
    return "CxFn1QSd0rRCQWieaf_e7pJiPrESsIaPqaYRHgUPpDs"


@pytest.fixture
def auth_headers(api_key):
    """Authentication headers with valid API key"""
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def test_user():
    """Test user data"""
    return {
        "user_id": "test_user_123",
        "session_id": "test_session_456"
    }


@pytest.fixture
def sample_product():
    """Sample product data"""
    return {
        "product_id": "P001",
        "name": "Test Product",
        "category": "test",
        "price": 99.99,
        "stock": 10
    }


@pytest.fixture
def sample_order():
    """Sample order data"""
    return {
        "order_id": "12345",
        "user_id": "test_user_123",
        "status": "delivered",
        "items": [
            {"product_id": "P001", "quantity": 2, "price": 99.99}
        ],
        "total_price": 199.98
    }


@pytest.fixture
def chat_payload(test_user):
    """Basic chat request payload"""
    return {
        "user_id": test_user["user_id"],
        "session_id": test_user["session_id"],
        "message": "Hello",
        "channel": "web"
    }
