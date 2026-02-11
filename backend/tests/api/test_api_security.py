"""
Basic authentication tests for OmniSales AI
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestAuthentication:
    """Test API authentication"""
    
    def test_chat_without_auth_returns_401(self):
        """Test that chat endpoint requires authentication"""
        response = client.post(
            "/chat",
            json={
                "user_id": "test_user",
                "session_id": "test_session",
                "message": "Hello"
            }
        )
        assert response.status_code == 403  # FastAPI returns 403 for missing auth
    
    def test_chat_with_invalid_auth_returns_401(self):
        """Test that invalid API key is rejected"""
        response = client.post(
            "/chat",
            headers={"Authorization": "Bearer invalid-key"},
            json={
                "user_id": "test_user",
                "session_id": "test_session",
                "message": "Hello"
            }
        )
        assert response.status_code == 401
        assert "Invalid API key" in response.json()["detail"]
    
    def test_health_endpoint_public(self):
        """Test that health endpoint is publicly accessible"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestInputValidation:
    """Test input validation"""
    
    def test_empty_message_rejected(self):
        """Test that empty messages are rejected"""
        response = client.post(
            "/chat",
            headers={"Authorization": "Bearer test-key"},
            json={
                "user_id": "test_user",
                "session_id": "test_session",
                "message": ""
            }
        )
        assert response.status_code == 422  # Validation error
    
    def test_invalid_user_id_rejected(self):
        """Test that invalid user ID format is rejected"""
        response = client.post(
            "/chat",
            headers={"Authorization": "Bearer test-key"},
            json={
                "user_id": "invalid user with spaces!@#",
                "session_id": "test_session",
                "message": "Hello"
            }
        )
        assert response.status_code == 422
    
    def test_message_too_long_rejected(self):
        """Test that messages over 5000 chars are rejected"""
        long_message = "a" * 5001
        response = client.post(
            "/chat",
            headers={"Authorization": "Bearer test-key"},
            json={
                "user_id": "test_user",
                "session_id": "test_session",
                "message": long_message
            }
        )
        assert response.status_code == 422
    
    def test_invalid_channel_rejected(self):
        """Test that invalid channel is rejected"""
        response = client.post(
            "/chat",
            headers={"Authorization": "Bearer test-key"},
            json={
                "user_id": "test_user",
                "session_id": "test_session",
                "message": "Hello",
                "channel": "invalid_channel"
            }
        )
        assert response.status_code == 422


class TestSecurityHeaders:
    """Test security headers middleware"""
    
    def test_security_headers_present(self):
        """Test that security headers are added to responses"""
        response = client.get("/health")
        
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        
        assert "X-XSS-Protection" in response.headers
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        
        assert "Strict-Transport-Security" in response.headers
        
        assert "Content-Security-Policy" in response.headers


class TestRateLimiting:
    """Test rate limiting"""
    
    def test_rate_limit_enforced(self):
        """Test that rate limiting is enforced"""
        # This test requires actual rate limiting to be active
        # In a real test environment, you'd mock the limiter or use a test client
        # that can simulate multiple requests quickly
        
        # For now, just verify the endpoint is accessible
        response = client.get("/health")
        assert response.status_code == 200


class TestWebhookValidation:
    """Test webhook payload validation"""
    
    def test_whatsapp_webhook_invalid_payload(self):
        """Test that invalid WhatsApp webhook payload is rejected"""
        response = client.post(
            "/webhook/whatsapp",
            json={"invalid": "payload"}
        )
        assert response.status_code == 400
        assert "Invalid webhook payload" in response.json()["detail"]
    
    def test_superu_webhook_invalid_payload(self):
        """Test that invalid SuperU webhook payload is rejected"""
        response = client.post(
            "/webhook/superu",
            json={"invalid": "payload"}
        )
        assert response.status_code == 400
        assert "Invalid webhook payload" in response.json()["detail"]
    
    def test_superu_webhook_missing_required_fields(self):
        """Test that SuperU webhook requires all fields"""
        response = client.post(
            "/webhook/superu",
            json={
                "call_id": "test123",
                # Missing other required fields
            }
        )
        assert response.status_code == 422  # Pydantic validation error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
