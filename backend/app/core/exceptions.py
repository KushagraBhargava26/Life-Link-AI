# backend/app/core/exceptions.py
# LifeLink AI — Global Exception Handlers
# Architecture Reference: ARCHITECTURE.md Section 37 (Error Handling Strategy)
#
# Defines:
#   - Base LifeLink exception hierarchy
#   - FastAPI exception handler registration
#   - Standard error response format (matching API envelope)
#
# All error responses follow the standard envelope:
# {
#   "success": false,
#   "error": { "code": "...", "message": "...", "details": {} },
#   "timestamp": "...",
#   "request_id": "..."
# }

from __future__ import annotations

import time
import uuid
from typing import Any

import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = structlog.get_logger(__name__)


# =============================================================================
# LifeLink Exception Hierarchy
# =============================================================================
class LifeLinkBaseException(Exception):
    """
    Base exception for all LifeLink AI application exceptions.

    Every custom exception in this codebase must inherit from this class.
    Architecture Rule: Never raise bare Exception() in production code.
    """

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


LifeLinkException = LifeLinkBaseException


class NotFoundError(LifeLinkBaseException):
    """Resource not found — maps to HTTP 404."""

    def __init__(self, message: str, code: str = "NOT_FOUND", details: dict[str, Any] | None = None) -> None:
        super().__init__(message, code, status.HTTP_404_NOT_FOUND, details)


class ConflictError(LifeLinkBaseException):
    """Resource conflict (e.g., duplicate, race condition) — maps to HTTP 409."""

    def __init__(self, message: str, code: str = "CONFLICT", details: dict[str, Any] | None = None) -> None:
        super().__init__(message, code, status.HTTP_409_CONFLICT, details)


class ValidationError(LifeLinkBaseException):
    """Business validation failure — maps to HTTP 422."""

    def __init__(self, message: str, code: str = "VALIDATION_ERROR", details: dict[str, Any] | None = None) -> None:
        super().__init__(message, code, status.HTTP_422_UNPROCESSABLE_ENTITY, details)


class UnauthorizedError(LifeLinkBaseException):
    """Authentication required or token invalid — maps to HTTP 401."""

    def __init__(self, message: str = "Authentication required", code: str = "UNAUTHORIZED") -> None:
        super().__init__(message, code, status.HTTP_401_UNAUTHORIZED)


class ForbiddenError(LifeLinkBaseException):
    """Authenticated but insufficient permissions — maps to HTTP 403."""

    def __init__(self, message: str = "You do not have permission to perform this action", code: str = "FORBIDDEN") -> None:
        super().__init__(message, code, status.HTTP_403_FORBIDDEN)


class ServiceUnavailableError(LifeLinkBaseException):
    """External service unavailable (AI, email, Firebase) — maps to HTTP 503."""

    def __init__(self, message: str, code: str = "SERVICE_UNAVAILABLE", details: dict[str, Any] | None = None) -> None:
        super().__init__(message, code, status.HTTP_503_SERVICE_UNAVAILABLE, details)


class InventoryLockError(LifeLinkBaseException):
    """
    Blood inventory locked by another request — maps to HTTP 409.

    Architecture Reference: ARCHITECTURE.md ADR-001 (Blood Inventory Concurrency Strategy)
    Raised when SELECT FOR UPDATE NOWAIT fails due to a concurrent reservation.
    """

    def __init__(self, message: str = "Blood inventory is currently locked by another request. Please retry.") -> None:
        super().__init__(message, "INVENTORY_LOCKED", status.HTTP_409_CONFLICT)


# =============================================================================
# Error Response Builder
# =============================================================================
def _build_error_response(
    code: str,
    message: str,
    status_code: int,
    details: dict[str, Any] | None = None,
    request_id: str | None = None,
) -> JSONResponse:
    """Build a standard error response envelope."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            },
            "timestamp": time.time(),
            "request_id": request_id or str(uuid.uuid4()),
        },
    )


# =============================================================================
# Exception Handler Registration
# =============================================================================
def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all global exception handlers on the FastAPI application.

    Called from app/main.py during application initialization.
    """

    @app.exception_handler(LifeLinkBaseException)
    async def lifelink_exception_handler(
        request: Request,
        exc: LifeLinkBaseException,
    ) -> JSONResponse:
        """Handle all LifeLink custom exceptions."""
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        logger.warning(
            "LifeLink exception",
            code=exc.code,
            message=exc.message,
            status_code=exc.status_code,
            request_id=request_id,
            path=str(request.url),
        )
        return _build_error_response(
            code=exc.code,
            message=exc.message,
            status_code=exc.status_code,
            details=exc.details,
            request_id=request_id,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        """Handle standard HTTP exceptions (404, 405, etc.)."""
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        code_map = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            409: "CONFLICT",
            422: "VALIDATION_ERROR",
            429: "RATE_LIMIT_EXCEEDED",
            500: "INTERNAL_ERROR",
            503: "SERVICE_UNAVAILABLE",
        }
        code = code_map.get(exc.status_code, "HTTP_ERROR")
        logger.info(
            "HTTP exception",
            code=code,
            status_code=exc.status_code,
            request_id=request_id,
            path=str(request.url),
        )
        return _build_error_response(
            code=code,
            message=str(exc.detail),
            status_code=exc.status_code,
            request_id=request_id,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """
        Handle Pydantic validation errors on request input.
        Returns a 422 with field-level error details.
        """
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        field_errors = []
        for error in exc.errors():
            field_errors.append({
                "field": " → ".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            })
        logger.info(
            "Request validation error",
            errors=field_errors,
            request_id=request_id,
            path=str(request.url),
        )
        return _build_error_response(
            code="REQUEST_VALIDATION_ERROR",
            message="Request validation failed. Check the 'details' field for per-field errors.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"fields": field_errors},
            request_id=request_id,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """
        Catch-all handler for unhandled exceptions.

        Never exposes internal exception details in production.
        Logs the full traceback for debugging.
        """
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        logger.exception(
            "Unhandled exception",
            exc_type=type(exc).__name__,
            request_id=request_id,
            path=str(request.url),
        )
        return _build_error_response(
            code="INTERNAL_ERROR",
            message="An unexpected error occurred. This has been logged and will be investigated.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            request_id=request_id,
        )
