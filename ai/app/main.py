# ai/app/main.py
# LifeLink AI — AI Inference Service Entry Point
# Architecture Reference: ARCHITECTURE.md Section 17 & Section 29
#
# This file:
#   - Creates the FastAPI application instance
#   - Configures logging and startup/shutdown lifecycle
#   - Registers matching, prediction, ocr, nlp routers
#   - Protects endpoints with API Key verification
#
# Phase 1.1: Scaffolding only — no business logic.

from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import JSONResponse
import structlog

from app.config import ai_settings

# Configure simple logging
logging_level = getattr(logging, ai_settings.LOG_LEVEL.upper(), logging.INFO)
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.stdlib.add_log_level,
        structlog.processors.JSONRenderer() if ai_settings.IS_PRODUCTION else structlog.dev.ConsoleRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging_level),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# API Key security scheme
API_KEY_NAME = "X-AI-Service-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def verify_api_key(
    api_key_val: str | None = Security(api_key_header),
) -> str:
    """Validate internal API key for request authentication."""
    if not api_key_val:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key missing in request headers.",
        )
    if api_key_val != ai_settings.AI_SERVICE_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key.",
        )
    return api_key_val


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Handles lifecycle events for AI models."""
    logger.info(
        "AI Service starting",
        app_name=ai_settings.APP_NAME,
        version=ai_settings.APP_VERSION,
        environment=ai_settings.APP_ENV,
    )
    # Phase 1.2+: Load scikit-learn compatibility matrix & rules
    # from ai.app.modules.matching.engine import MatchingEngine
    # app.state.matching_engine = MatchingEngine()
    # await app.state.matching_engine.load()
    yield
    logger.info("AI Service shutting down")


app = FastAPI(
    title=ai_settings.APP_NAME,
    description="LifeLink AI Inference Service (Internal Only)",
    version=ai_settings.APP_VERSION,
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Router Registration
# ---------------------------------------------------------------------------
from app.modules.matching.router import router as matching_router
from app.modules.prediction.router import router as prediction_router
from app.modules.ocr.router import router as ocr_router
from app.modules.nlp.router import router as nlp_router

# All core AI routes require API key verification
app.include_router(
    matching_router,
    prefix="/matching",
    tags=["Matching"],
    dependencies=[Depends(verify_api_key)],
)
app.include_router(
    prediction_router,
    prefix="/prediction",
    tags=["Prediction"],
    dependencies=[Depends(verify_api_key)],
)
app.include_router(
    ocr_router,
    prefix="/ocr",
    tags=["OCR"],
    dependencies=[Depends(verify_api_key)],
)
app.include_router(
    nlp_router,
    prefix="/nlp",
    tags=["NLP"],
    dependencies=[Depends(verify_api_key)],
)


@app.get(
    "/health",
    tags=["Health"],
    summary="AI service health check",
)
async def health_check() -> JSONResponse:
    """Return health status of the AI service."""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "success": True,
            "data": {
                "service": "ai-service",
                "status": "healthy",
                "timestamp": time.time(),
            },
            "message": "LifeLink AI inference service is running",
        },
    )
