import uuid
import logging
from starlette.datastructures import MutableHeaders
from app.utils.logging_context import set_request_id, reset_request_id

logger = logging.getLogger(__name__)


class RequestIdMiddleware:
    """Attach a request ID to each response and log context."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = scope.get("headers")
        request_id_value = None

        # Attempt to read incoming request id header
        for key, value in scope.get("headers", []):
            if key == b"x-request-id":
                request_id_value = value.decode("utf-8")
                break

        if not request_id_value:
            request_id_value = str(uuid.uuid4())

        async def send_with_request_id(message):
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers["X-Request-ID"] = request_id_value
            await send(message)

        scope["request_id"] = request_id_value
        token = set_request_id(request_id_value)
        logger.info("Request start", extra={"path": scope.get("path")})

        try:
            await self.app(scope, receive, send_with_request_id)
        finally:
            reset_request_id(token)
