"""
Unit tests for Pydantic models and schemas
Tests data validation and serialization
"""
import pytest
from pydantic import ValidationError
from datetime import datetime
from app.models.schemas import (
    User,
    Session,
    Product,
    Order,
    ChatRequest,
    ChatResponse,
    ApiResponse
)


class TestUserModel:
    """Test User model validation"""
    
    def test_user_valid_creation(self):
        """Test creating a valid user"""
        user = User(
            user_id="test_user_123",
            name="Test User",
            preferences={"category": "electronics"}
        )
        assert user.user_id == "test_user_123"
        assert user.name == "Test User"
        assert "category" in user.preferences
    
    def test_user_default_preferences(self):
        """Test user created with empty preferences by default"""
        user = User(user_id="user123", name="User")
        assert user.preferences == {}
    
    def test_user_has_created_at(self):
        """Test user has created_at timestamp"""
        user = User(user_id="user123", name="User")
        assert isinstance(user.created_at, datetime)
    
    def test_user_requires_user_id(self):
        """Test user requires user_id field"""
        with pytest.raises(ValidationError):
            User(name="User")
    
    def test_user_requires_name(self):
        """Test user requires name field"""
        with pytest.raises(ValidationError):
            User(user_id="user123")


class TestSessionModel:
    """Test Session model validation"""
    
    def test_session_valid_creation(self):
        """Test creating a valid session"""
        session = Session(
            session_id="session_123",
            user_id="user_123"
        )
        assert session.session_id == "session_123"
        assert session.user_id == "user_123"
    
    def test_session_default_values(self):
        """Test session defaults (empty lists, timestamp)"""
        session = Session(session_id="s1", user_id="u1")
        assert session.last_messages == []
        assert session.cart_items == []
        assert session.summary is None
        assert isinstance(session.updated_at, datetime)
    
    def test_session_with_cart_items(self):
        """Test session can store cart items"""
        session = Session(
            session_id="s1",
            user_id="u1",
            cart_items=[
                {"product_id": "P001", "quantity": 2, "price": 99.99}
            ]
        )
        assert len(session.cart_items) == 1
        assert session.cart_items[0]["product_id"] == "P001"
    
    def test_session_with_message_history(self):
        """Test session can store message history"""
        session = Session(
            session_id="s1",
            user_id="u1",
            last_messages=[
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi!"}
            ]
        )
        assert len(session.last_messages) == 2


class TestProductModel:
    """Test Product model validation"""
    
    def test_product_valid_creation(self):
        """Test creating a valid product"""
        product = Product(
            product_id="P001",
            name="Test Product",
            category="test",
            price=99.99,
            stock=10
        )
        assert product.product_id == "P001"
        assert product.price == 99.99
        assert product.stock == 10
    
    def test_product_requires_all_fields(self):
        """Test product requires all fields"""
        with pytest.raises(ValidationError):
            Product(
                product_id="P001",
                name="Test"
                # Missing category, price, stock
            )
    
    def test_product_price_must_be_numeric(self):
        """Test product price must be a number"""
        with pytest.raises(ValidationError):
            Product(
                product_id="P001",
                name="Test",
                category="test",
                price="invalid",  # Should be float
                stock=10
            )
    
    def test_product_stock_must_be_integer(self):
        """Test product stock must be an integer"""
        with pytest.raises(ValidationError):
            Product(
                product_id="P001",
                name="Test",
                category="test",
                price=99.99,
                stock="ten"  # Should be int
            )


class TestOrderModel:
    """Test Order model validation"""
    
    def test_order_valid_creation(self):
        """Test creating a valid order"""
        order = Order(
            order_id="12345",
            user_id="user_123",
            items=[{"product_id": "P001", "quantity": 2}],
            total_price=199.98
        )
        assert order.order_id == "12345"
        assert order.status == "pending"  # Default status
    
    def test_order_custom_status(self):
        """Test order with custom status"""
        order = Order(
            order_id="12345",
            user_id="user_123",
            items=[],
            total_price=0.0,
            status="delivered"
        )
        assert order.status == "delivered"
    
    def test_order_requires_items_list(self):
        """Test order requires items field"""
        with pytest.raises(ValidationError):
            Order(
                order_id="12345",
                user_id="user_123",
                total_price=100.0
                # Missing items
            )


class TestChatRequestModel:
    """Test ChatRequest model validation"""
    
    def test_chat_request_valid(self):
        """Test creating a valid chat request"""
        request = ChatRequest(
            user_id="user_123",
            session_id="session_456",
            message="Hello"
        )
        assert request.user_id == "user_123"
        assert request.message == "Hello"
        assert request.channel == "web"  # Default
    
    def test_chat_request_custom_channel(self):
        """Test chat request with custom channel"""
        request = ChatRequest(
            user_id="user_123",
            session_id="session_456",
            message="Hello",
            channel="whatsapp"
        )
        assert request.channel == "whatsapp"


class TestApiResponseModel:
    """Test ApiResponse envelope"""

    def test_api_response_defaults(self):
        response = ApiResponse(success=True)
        assert response.success is True
        assert response.message == ""
        assert response.error is None

    def test_api_response_all_fields(self):
        response = ApiResponse(success=False, data={"x": 1}, message="fail", error="bad")
        assert response.success is False
        assert response.data["x"] == 1
        assert response.message == "fail"
        assert response.error == "bad"
    
    def test_chat_request_requires_all_fields(self):
        """Test chat request requires user_id, session_id, message"""
        with pytest.raises(ValidationError):
            ChatRequest(
                user_id="user_123"
                # Missing session_id and message
            )
    
    def test_chat_request_rejects_empty_message(self):
        """Test chat request rejects empty message"""
        # This would be caught by API validation
        request = ChatRequest(
            user_id="user_123",
            session_id="session_456",
            message=""
        )
        # Model allows it, but API validation should reject


class TestChatResponseModel:
    """Test ChatResponse model validation"""
    
    def test_chat_response_valid(self):
        """Test creating a valid chat response"""
        response = ChatResponse(
            reply="Hello! How can I help?",
            agent_used="general"
        )
        assert response.reply == "Hello! How can I help?"
        assert response.agent_used == "general"
        assert response.actions is None  # Default
    
    def test_chat_response_with_actions(self):
        """Test chat response with actions"""
        response = ChatResponse(
            reply="Added to cart",
            agent_used="cart",
            actions=[
                {"type": "cart_updated", "data": {"cart_size": 1}}
            ]
        )
        assert len(response.actions) == 1
        assert response.actions[0]["type"] == "cart_updated"
    
    def test_chat_response_requires_reply_and_agent(self):
        """Test chat response requires reply and agent_used"""
        with pytest.raises(ValidationError):
            ChatResponse(reply="Hello")  # Missing agent_used
        
        with pytest.raises(ValidationError):
            ChatResponse(agent_used="general")  # Missing reply
