"""
Shared test fixtures and configuration
"""
import os
import importlib
from types import SimpleNamespace
import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("API_SECRET_KEY", "test-api-key")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "omnisales_test")
os.environ.setdefault("WHATSAPP_VERIFY_TOKEN", "test_token")


class FakeCollection:
    async def create_index(self, *args, **kwargs):
        return None

    async def find_one(self, *args, **kwargs):
        return None

    async def update_one(self, *args, **kwargs):
        return SimpleNamespace(matched_count=1, modified_count=1)

    async def insert_one(self, *args, **kwargs):
        return SimpleNamespace(inserted_id="test_id")

    async def delete_one(self, *args, **kwargs):
        return SimpleNamespace(deleted_count=1)

    def find(self, *args, **kwargs):
        return SimpleNamespace(
            sort=lambda *a, **k: SimpleNamespace(
                skip=lambda *a, **k: SimpleNamespace(
                    limit=lambda *a, **k: SimpleNamespace(
                        to_list=lambda length=0: []
                    )
                )
            )
        )


class FakeDatabase:
    def __init__(self):
        self.users = FakeCollection()
        self.sessions = FakeCollection()
        self.products = FakeCollection()
        self.orders = FakeCollection()
        self.offers = FakeCollection()
        self.reviews = FakeCollection()

    async def command(self, *args, **kwargs):
        return {"ok": 1}


@pytest.fixture
def client(monkeypatch):
    """FastAPI test client with fake DB and test settings"""
    os.environ.setdefault("API_SECRET_KEY", "test-api-key")
    os.environ.setdefault("SECRET_KEY", "test-secret")
    os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017")
    os.environ.setdefault("DB_NAME", "omnisales_test")
    os.environ.setdefault("WHATSAPP_VERIFY_TOKEN", "test_token")

    from app import core
    from app.core import database as db

    fake_db = FakeDatabase()

    async def fake_connect_db(*args, **kwargs):
        return None

    async def fake_close_db(*args, **kwargs):
        return None

    monkeypatch.setattr(db, "connect_db", fake_connect_db)
    monkeypatch.setattr(db, "close_db", fake_close_db)
    monkeypatch.setattr(db, "get_database", lambda: fake_db)

    import app.main as main
    importlib.reload(main)

    return TestClient(main.app)


@pytest.fixture
def api_key():
    """Valid API key for testing"""
    return "test-api-key"


@pytest.fixture
def auth_headers(api_key):
    """Authentication headers with valid API key"""
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def user_token(test_user):
    """JWT token for authenticated user flows"""
    from app.auth import create_access_token

    return create_access_token({"user_id": test_user["user_id"]})


@pytest.fixture
def user_token_headers(user_token):
    """Headers for authenticated web chat requests"""
    return {
        "X-User-Token": user_token,
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


@pytest.fixture
def mock_chat_dependencies(monkeypatch):
    """Mock chat routing and persistence to avoid external calls."""
    async def fake_route_request(*args, **kwargs):
        return {"reply": "ok", "agent_used": "general", "actions": None}

    async def fake_save_message(*args, **kwargs):
        return None

    import app.orchestrator.router as router
    import app.repositories.session_repository as session_repo

    monkeypatch.setattr(router, "route_request", fake_route_request)
    monkeypatch.setattr(session_repo, "save_message", fake_save_message)

    return True
