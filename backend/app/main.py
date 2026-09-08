# backend/app/main.py
# LifeLink AI — FastAPI Application Entry Point
# Architecture Reference: ARCHITECTURE.md Section 16 (Backend Architecture)
#
# This file:
#   - Creates the FastAPI application instance
#   - Registers all module routers (Phase 1.2+)
#   - Attaches global middleware
#   - Defines health check endpoint
#
# Phase 1.1: Scaffolding only — no business logic, no endpoints implemented.

from __future__ import annotations

import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.core.middleware import RateLimitMiddleware, RequestLoggingMiddleware

# ---------------------------------------------------------------------------
# Configure structured logging before anything else
# ---------------------------------------------------------------------------
configure_logging()

import structlog  # noqa: E402 — must be after configure_logging()

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Application Lifespan — startup and shutdown events
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager.

    Handles:
    - Database connection pool initialization
    - Redis connection initialization
    - Graceful shutdown of connections

    Note: In Phase 1.1, connections are not yet initialized.
    Full implementation occurs in Phase 1.2.
    """
    # -----------------------------------------------------------------------
    # STARTUP
    # -----------------------------------------------------------------------
    logger.info(
        "LifeLink AI backend starting",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
    )

    # Phase 1.2+: Initialize database connection pool
    from app.database import init_db
    await init_db()

    # Phase 1.2+: Initialize Redis connection
    from app.core.redis import init_redis
    await init_redis()

    logger.info("LifeLink AI backend startup complete")

    yield  # Application runs here

    # -----------------------------------------------------------------------
    # SHUTDOWN
    # -----------------------------------------------------------------------
    logger.info("LifeLink AI backend shutting down")

    # Phase 1.2+: Close database connection pool
    from app.database import close_db
    await close_db()

    # Phase 1.2+: Close Redis connection
    from app.core.redis import close_redis
    await close_redis()

    logger.info("LifeLink AI backend shutdown complete")


# ---------------------------------------------------------------------------
# FastAPI Application Instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "AI-Powered Emergency Blood and Organ Intelligence Platform. "
        "Connects patients, donors, hospitals, and blood banks in real time."
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    # Contact and license metadata for API docs
    contact={
        "name": "LifeLink AI Team",
        "email": "dev@lifelink.ai",
    },
    license_info={
        "name": "Proprietary",
    },
)

# ---------------------------------------------------------------------------
# Middleware Stack
# Architecture Reference: ARCHITECTURE.md Section 16 (Middleware Stack)
# Processing order (first registered = outermost wrapper):
#   1. CORS
#   2. Rate Limiting (Redis-backed)
#   3. Request Logging (assigns request_id)
#   4. JWT Auth (in dependency injection, not middleware layer)
# ---------------------------------------------------------------------------

# 1. CORS Middleware — must be first
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
)

# 2. Rate Limiting Middleware
app.add_middleware(RateLimitMiddleware)

# 3. Request Logging Middleware
app.add_middleware(RequestLoggingMiddleware)

# ---------------------------------------------------------------------------
# Global Exception Handlers
# Architecture Reference: ARCHITECTURE.md Section 37 (Error Handling Strategy)
# ---------------------------------------------------------------------------
register_exception_handlers(app)

# ---------------------------------------------------------------------------
# Module Router Registration
# Architecture Reference: ARCHITECTURE.md Section 22 (Complete Module Breakdown)
#
# Phase 1.1: Routers exist as empty files. No routes registered yet.
# Phase 1.2+: Uncomment each router as the module is implemented.
# ---------------------------------------------------------------------------
API_V1_PREFIX = "/api/v1"

from app.modules.auth.router import router as auth_router
from app.modules.donor.router import router as donor_router
from app.modules.hospital.router import router as hospital_router
from app.modules.blood_bank.router import router as blood_bank_router
from app.modules.inventory.router import blood_bank_inventory_router, inventory_router
from app.modules.emergency.router import router as emergency_router
from app.modules.matching.router import router as matching_router
from app.modules.admin.router import router as admin_router
# from app.modules.notification.router import router as notification_router
# from app.modules.ai_gateway.router import router as ai_gateway_router
# from app.modules.analytics.router import router as analytics_router

app.include_router(auth_router, prefix=f"{API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(donor_router, prefix=f"{API_V1_PREFIX}/donors", tags=["Donors"])
app.include_router(hospital_router, prefix=f"{API_V1_PREFIX}/hospitals", tags=["Hospitals"])
app.include_router(blood_bank_router, prefix=f"{API_V1_PREFIX}/blood-banks", tags=["Blood Banks"])
app.include_router(blood_bank_inventory_router, prefix=f"{API_V1_PREFIX}/blood-banks", tags=["Blood Bank Inventory"])
app.include_router(inventory_router, prefix=f"{API_V1_PREFIX}/inventory", tags=["Inventory"])
app.include_router(emergency_router, prefix=f"{API_V1_PREFIX}/emergency", tags=["Emergency"])
app.include_router(matching_router, prefix=f"{API_V1_PREFIX}/emergency", tags=["Matching & Coordination"])
app.include_router(matching_router, prefix=f"{API_V1_PREFIX}/matching", tags=["Matching & Coordination"])
app.include_router(matching_router, prefix=f"{API_V1_PREFIX}/hospitals/me", tags=["Matching & Coordination"])
app.include_router(admin_router, prefix=f"{API_V1_PREFIX}/admin", tags=["Admin"])
# app.include_router(notification_router, prefix=f"{API_V1_PREFIX}/notifications", tags=["Notifications"])
# app.include_router(ai_gateway_router, prefix=f"{API_V1_PREFIX}/ai", tags=["AI Gateway"])
# app.include_router(analytics_router, prefix=f"{API_V1_PREFIX}/analytics", tags=["Analytics"])



# ---------------------------------------------------------------------------
# Health Check Endpoint
# Required by Docker Compose healthcheck and Nginx upstream checks
# ---------------------------------------------------------------------------
@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    response_description="Service health status",
)
async def health_check() -> JSONResponse:
    """
    Health check endpoint.

    Returns the current health status of the backend service.
    Used by Docker Compose, load balancers, and monitoring systems.

    This endpoint is intentionally lightweight — it does not check
    database or Redis connectivity. Use /health/detailed for deep checks.
    """
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "data": {
                "service": "backend",
                "status": "healthy",
                "app_name": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "environment": settings.APP_ENV,
                "timestamp": time.time(),
            },
            "message": "LifeLink AI backend is running",
        },
    )


@app.get(
    "/",
    tags=["Root"],
    summary="API root",
    include_in_schema=False,  # Don't show in Swagger docs
)
async def root() -> JSONResponse:
    """API root — redirects users to the documentation."""
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "data": {
                "name": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "docs": "/docs",
                "redoc": "/redoc",
                "health": "/health",
            },
            "message": "Welcome to LifeLink AI API. See /docs for full documentation.",
        },
    )
