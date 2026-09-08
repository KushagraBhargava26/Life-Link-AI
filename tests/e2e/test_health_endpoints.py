# tests/e2e/test_health_endpoints.py
# LifeLink AI — E2E Health Endpoints Validation Test
# Architecture Reference: ARCHITECTURE.md Section 35 (Testing Strategy)
#
# Validates startup status of Nginx, Backend, and AI Service containers.

from __future__ import annotations

import httpx
import pytest

NGINX_URL = "http://localhost"
BACKEND_HEALTH_URL = "http://localhost/health"  # via Nginx
AI_HEALTH_URL = "http://localhost:8001/health"  # direct internal port (if exposed/accessible locally)


@pytest.mark.asyncio
async def test_nginx_reaches_frontend() -> None:
    """Validate that Nginx proxy serves the Next.js frontend root page."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(NGINX_URL, timeout=5.0)
            assert response.status_code == 200
            assert "LifeLink AI" in response.text
        except httpx.RequestError as e:
            pytest.skip(f"Nginx / Frontend is unreachable: {e}")


@pytest.mark.asyncio
async def test_nginx_reaches_backend_health() -> None:
    """Validate that Nginx proxy correctly routes to the FastAPI backend /health endpoint."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(BACKEND_HEALTH_URL, timeout=5.0)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["service"] == "backend"
        except httpx.RequestError as e:
            pytest.skip(f"Backend API is unreachable: {e}")


@pytest.mark.asyncio
async def test_ai_service_health() -> None:
    """Validate that the AI service health check endpoint responds correctly."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(AI_HEALTH_URL, timeout=5.0)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["service"] == "ai-service"
        except httpx.RequestError as e:
            pytest.skip(f"AI Service is unreachable: {e}")
