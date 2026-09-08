# backend/app/core/middleware.py
# LifeLink AI — Application Middleware
# Architecture Reference: ARCHITECTURE.md Section 16 (Middleware Stack)
#
# Middleware processing order (registered in main.py):
#   1. CORS Middleware (registered via FastAPI's built-in)
#   2. Rate Limiting Middleware (Redis-backed, per IP)
#   3. Request Logging Middleware (assigns request_id, logs timing)
#
# Phase 1.1: Structural implementation — Redis calls are stubbed where Redis
# connection is not yet initialized.

from __future__ import annotations

import time
import uuid

from typing import Any

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = structlog.get_logger(__name__)


# =============================================================================
# Request Logging Middleware
# =============================================================================
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Log every incoming request with a unique request_id and response timing.

    Architecture Reference: ARCHITECTURE.md Section 36 (Logging Strategy)

    Assigns a request_id to every request via the X-Request-ID header.
    If the client provides an X-Request-ID, it is used; otherwise a new UUID is generated.
    The request_id is bound to all log entries for that request via structlog.contextvars.
    """

    async def dispatch(self, request: Request, call_next: Any) -> Response:  # type: ignore[override]
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        start_time = time.perf_counter()

        # Bind request_id to all log entries within this request lifecycle
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )

        logger.info(
            "Request received",
            client_ip=request.client.host if request.client else "unknown",
        )

        response = await call_next(request)

        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            "Request completed",
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
        )

        # Attach request_id to response header for tracing
        response.headers["X-Request-ID"] = request_id

        return response


# =============================================================================
# Rate Limiting Middleware
# =============================================================================
class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Redis-backed rate limiting middleware.

    Architecture Reference: ARCHITECTURE.md Section 16 (Rate Limiting Middleware)
    - General API: 100 requests per minute per IP (settings.RATE_LIMIT_GENERAL)
    - Login: 5 failed attempts per 15 minutes per IP (settings.RATE_LIMIT_LOGIN)
    - Register: 10 registrations per hour per IP (settings.RATE_LIMIT_REGISTER)

    Phase 1.1: Structural implementation — rate limit check is stubbed.
    Phase 1.2+: Wire up Redis client for actual counting.

    Cache key pattern: ratelimit:{ip}:{endpoint}
    Architecture Reference: ARCHITECTURE.md Section 25 (Caching Strategy)
    """

    # Paths excluded from rate limiting
    EXCLUDED_PATHS = {"/health", "/docs", "/redoc", "/openapi.json", "/"}

    async def dispatch(self, request: Request, call_next: Any) -> Response:  # type: ignore[override]
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"

        # Phase 1.2+: Implement Redis-backed rate limit check
        # from app.core.redis import get_redis
        # redis_client = get_redis()
        # key = f"v1:ratelimit:{client_ip}:{request.url.path}"
        # count = await redis_client.incr(key)
        # if count == 1:
        #     await redis_client.expire(key, 60)
        # limit = settings.RATE_LIMIT_GENERAL
        # if count > limit:
        #     return JSONResponse(
        #         status_code=429,
        #         content={"success": False, "error": {"code": "RATE_LIMIT_EXCEEDED", "message": "Rate limit exceeded. Retry after 60 seconds."}}
        #     )

        return await call_next(request)



