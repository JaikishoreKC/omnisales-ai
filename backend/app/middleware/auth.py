"""Authentication middleware for API security"""
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.datastructures import MutableHeaders
from typing import Optional
import secrets
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials,
    settings
) -> bool:
    """
    Verify API key from Authorization header.
    
    Args:
        credentials: Bearer token credentials
        settings: Application settings
        
    Returns:
        True if valid, raises HTTPException if invalid
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials"
        )
    
    if not settings.api_secret_key:
        logger.error("API_SECRET_KEY is not configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server auth misconfiguration"
        )

    # Verify against API_SECRET_KEY from .env
    if not secrets.compare_digest(credentials.credentials, settings.api_secret_key):
        logger.warning(f"Invalid API key attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return True


async def verify_webhook_signature(
    request: Request,
    expected_token: str,
    header_name: str = "X-Hub-Signature-256"
) -> bool:
    """
    Verify webhook signature from external services.
    
    Args:
        request: FastAPI request object
        expected_token: Expected signature/token
        header_name: Name of signature header
        
    Returns:
        True if valid, raises HTTPException if invalid
    """
    if not expected_token:
        logger.error("Webhook signature secret is not configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook auth misconfiguration"
        )

    signature = request.headers.get(header_name)
    
    if not signature:
        logger.warning(f"Missing webhook signature header: {header_name}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing webhook signature"
        )
    
    # For WhatsApp, Meta sends signatures
    # For SuperU, implement their signature verification
    # Simple token check for now
    if not secrets.compare_digest(signature, expected_token):
        logger.warning(f"Invalid webhook signature")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature"
        )
    
    return True


class SecurityHeadersMiddleware:
    """Add security headers to all responses"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers["X-Content-Type-Options"] = "nosniff"
                headers["X-Frame-Options"] = "DENY"
                headers["X-XSS-Protection"] = "1; mode=block"
                headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
                # Relaxed CSP for FastAPI docs (Swagger UI) while maintaining security
                headers["Content-Security-Policy"] = (
                    "default-src 'self'; "
                    "style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
                    "script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
                    "img-src 'self' https://fastapi.tiangolo.com data:; "
                    "font-src 'self' https://cdn.jsdelivr.net; "
                    "connect-src 'self' https://cdn.jsdelivr.net;"
                )
            await send(message)
        
        await self.app(scope, receive, send_with_headers)
