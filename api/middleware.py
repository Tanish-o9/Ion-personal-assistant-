import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from orchestrator.observability import (
    generate_request_id,
    set_trace_context,
    default_metrics,
    jarvis_logger,
)

class RequestTracingMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for request ID correlation, duration measurement, metric collection, and structured access logging.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        client_req_id = request.headers.get("X-Request-ID")
        request_id = client_req_id if (client_req_id and len(client_req_id) <= 64) else generate_request_id()

        set_trace_context(request_id=request_id)
        endpoint_path = request.url.path

        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000
            response.headers["X-Request-ID"] = request_id

            default_metrics.record_request(endpoint=endpoint_path, status_code=response.status_code, duration_ms=duration_ms)
            jarvis_logger.info(
                f"HTTP {request.method} {endpoint_path} -> {response.status_code} ({round(duration_ms, 2)}ms)",
                extra={"request_id": request_id, "duration_ms": round(duration_ms, 2), "event": "http_request"},
            )
            return response
        except Exception as exc:
            duration_ms = (time.time() - start_time) * 1000
            default_metrics.record_request(endpoint=endpoint_path, status_code=500, duration_ms=duration_ms)
            jarvis_logger.error(
                f"HTTP {request.method} {endpoint_path} failed: {str(exc)}",
                extra={"request_id": request_id, "duration_ms": round(duration_ms, 2), "event": "http_error", "error": str(exc)},
            )
            raise exc
