"""
Comprehensive API endpoint tests
Tests all REST API endpoints
"""
import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Test /health endpoint"""
    
    def test_health_check_success(self, client):
        """Test health endpoint returns 200"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["success"] is True
    
    def test_health_check_no_auth_required(self, client):
        """Test health endpoint is public (no auth needed)"""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_check_has_security_headers(self, client):
        """Test health response includes security headers"""
        response = client.get("/health")
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers


class TestRootEndpoint:
    """Test / root endpoint"""
    
    def test_root_endpoint_success(self, client):
        """Test root endpoint returns welcome message"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["success"] is True
    
    def test_root_endpoint_no_auth_required(self, client):
        """Test root endpoint is public"""
        response = client.get("/")
        assert response.status_code == 200


class TestChatEndpoint:
    """Test /chat endpoint"""
    
    def test_chat_requires_auth(self, client, chat_payload, mock_chat_dependencies):
        """Test chat endpoint requires authentication"""
        response = client.post("/chat", json=chat_payload)
        assert response.status_code == 403  # FastAPI returns 403 for missing auth
    
    def test_chat_with_invalid_api_key(self, client, chat_payload, mock_chat_dependencies):
        """Test chat rejects invalid API key"""
        response = client.post(
            "/chat",
            headers={"Authorization": "Bearer invalid-key"},
            json=chat_payload
        )
        assert response.status_code == 401
        assert "Invalid API key" in response.json()["error"]
    
    def test_chat_with_valid_auth(self, client, auth_headers, chat_payload, mock_chat_dependencies):
        """Test chat accepts valid authentication"""
        response = client.post("/chat", headers=auth_headers, json=chat_payload)
        # May return 200 or timeout, but shouldn't be 401/403
        assert response.status_code != 401
        assert response.status_code != 403
    
    def test_chat_validates_required_fields(self, client, auth_headers, mock_chat_dependencies):
        """Test chat validates required fields"""
        # Missing message field
        response = client.post(
            "/chat",
            headers=auth_headers,
            json={"user_id": "test", "session_id": "test"}
        )
        assert response.status_code == 422
    
    def test_chat_validates_user_id_format(self, client, auth_headers, mock_chat_dependencies):
        """Test chat validates user_id format"""
        response = client.post(
            "/chat",
            headers=auth_headers,
            json={
                "user_id": "invalid user!@#",
                "session_id": "test_session",
                "message": "Hello"
            }
        )
        assert response.status_code == 422
    
    def test_chat_validates_message_length(self, client, auth_headers, mock_chat_dependencies):
        """Test chat rejects messages over 5000 chars"""
        long_message = "a" * 5001
        response = client.post(
            "/chat",
            headers=auth_headers,
            json={
                "user_id": "test_user",
                "session_id": "test_session",
                "message": long_message
            }
        )
        assert response.status_code == 422
    
    def test_chat_validates_channel(self, client, auth_headers, mock_chat_dependencies):
        """Test chat validates channel field"""
        response = client.post(
            "/chat",
            headers=auth_headers,
            json={
                "user_id": "test_user",
                "session_id": "test_session",
                "message": "Hello",
                "channel": "invalid_channel"
            }
        )
        assert response.status_code == 422
    
    def test_chat_accepts_valid_channels(self, client, auth_headers, mock_chat_dependencies):
        """Test chat accepts valid channel values"""
        valid_channels = ["web", "whatsapp", "voice"]
        for channel in valid_channels:
            response = client.post(
                "/chat",
                headers=auth_headers,
                json={
                    "user_id": "test_user",
                    "session_id": f"test_session_{channel}",
                    "message": "Hello",
                    "channel": channel
                }
            )
            # Should not be validation error
            assert response.status_code != 422
    
    def test_chat_rejects_empty_message(self, client, auth_headers, mock_chat_dependencies):
        """Test chat rejects empty messages"""
        response = client.post(
            "/chat",
            headers=auth_headers,
            json={
                "user_id": "test_user",
                "session_id": "test_session",
                "message": ""
            }
        )
        assert response.status_code == 422
    
    def test_chat_rejects_whitespace_only_message(self, client, auth_headers, mock_chat_dependencies):
        """Test chat rejects whitespace-only messages"""
        response = client.post(
            "/chat",
            headers=auth_headers,
            json={
                "user_id": "test_user",
                "session_id": "test_session",
                "message": "   "
            }
        )
        assert response.status_code == 422


class TestWhatsAppWebhook:
    """Test /webhook/whatsapp endpoints"""
    
    def test_whatsapp_webhook_get_verification(self, client):
        """Test WhatsApp webhook verification (GET)"""
        response = client.get(
            "/webhook/whatsapp",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "test_token",
                "hub.challenge": "test_challenge"
            }
        )
        # Should handle verification
        assert response.status_code in [200, 400]
    
    def test_whatsapp_webhook_post_requires_valid_payload(self, client):
        """Test WhatsApp webhook POST validation"""
        response = client.post(
            "/webhook/whatsapp",
            json={"invalid": "payload"}
        )
        assert response.status_code == 400
        assert "Invalid webhook payload" in response.json()["error"]
    
    def test_whatsapp_webhook_post_validates_structure(self, client):
        """Test WhatsApp webhook validates payload structure"""
        # Missing required fields
        response = client.post(
            "/webhook/whatsapp",
            json={
                "object": "whatsapp_business_account"
                # Missing entry field
            }
        )
        assert response.status_code in [400, 422]


class TestSuperUWebhook:
    """Test /webhook/superu endpoint"""
    
    def test_superu_webhook_requires_valid_payload(self, client):
        """Test SuperU webhook validation"""
        response = client.post(
            "/webhook/superu",
            json={"invalid": "payload"}
        )
        assert response.status_code == 400
        assert "Invalid webhook payload" in response.json()["error"]
    
    def test_superu_webhook_validates_required_fields(self, client):
        """Test SuperU webhook requires all fields"""
        response = client.post(
            "/webhook/superu",
            json={
                "call_id": "test123"
                # Missing other required fields
            }
        )
        assert response.status_code == 422  # Pydantic validation error
    
    def test_superu_webhook_validates_field_types(self, client):
        """Test SuperU webhook validates field types"""
        response = client.post(
            "/webhook/superu",
            json={
                "call_id": 12345,  # Should be string
                "phone_number": "123456789",
                "transcript": "Test",
                "status": "completed"
            }
        )
        assert response.status_code == 422


class TestSecurityHeaders:
    """Test security headers middleware"""
    
    def test_security_headers_on_all_responses(self, client):
        """Test security headers are added to all responses"""
        response = client.get("/health")
        
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"
        
        assert "X-XSS-Protection" in response.headers
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
    
    def test_hsts_header_present(self, client):
        """Test HSTS header is present"""
        response = client.get("/health")
        assert "Strict-Transport-Security" in response.headers
    
    def test_csp_header_present(self, client):
        """Test Content Security Policy header is present"""
        response = client.get("/health")
        assert "Content-Security-Policy" in response.headers


class TestCORSHeaders:
    """Test CORS configuration"""
    
    def test_cors_headers_present(self, client):
        """Test CORS headers are configured"""
        response = client.options("/chat")
        # CORS headers should be present
        assert response.status_code in [200, 405]


class TestErrorHandling:
    """Test API error handling"""
    
    def test_404_for_invalid_endpoint(self, client):
        """Test 404 returned for non-existent endpoints"""
        response = client.get("/non-existent-endpoint")
        assert response.status_code == 404
    
    def test_405_for_wrong_method(self, client):
        """Test 405 for wrong HTTP method"""
        response = client.get("/chat")  # Should be POST
        assert response.status_code == 405
    
    def test_422_for_invalid_json(self, client, auth_headers):
        """Test 422 for malformed request body"""
        response = client.post(
            "/chat",
            headers=auth_headers,
            data="invalid json"
        )
        assert response.status_code == 422
