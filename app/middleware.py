"""ASGI middleware: request-id tagging and access logging."""

from __future__ import annotations

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.logging import get_logger, log_event, set_request_id

logger = get_logger("http")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach a request id to each request and emit a timed access log."""

    async def dispatch(self, request: Request, call_next) -> Response:  # noqa: ANN001
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        set_request_id(request_id)
        start = time.perf_counter()
        try:
            response = await call_next(request)
        finally:
            set_request_id(None)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        log_event(
            logger,
            "request.completed",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=duration_ms,
        )
        return response
