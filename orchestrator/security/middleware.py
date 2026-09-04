from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from orchestrator.security.config import MAX_REQUEST_BODY_BYTES
from orchestrator.observability import jarvis_logger

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware applying HTTP security headers and enforcing request payload body size limits.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        # Enforce maximum body payload limit
        content_length = request.headers.get("Content-Length")
        if content_length and int(content_length) > MAX_REQUEST_BODY_BYTES:
            jarvis_logger.warning("Request body too large: %s bytes", content_length, extra={"event": "oversized_request"})
            return Response(content="Payload Too Large", status_code=413)

        response = await call_next(request)

        # Apply security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response
