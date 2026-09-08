# backend/tests/test_health.py
# LifeLink AI — Backend Health Endpoint Unit Test
# Architecture Reference: ARCHITECTURE.md Section 35 (Testing Strategy)

from __future__ import annotations

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check() -> None:
    """Validate that the standard /health endpoint returns HTTP 200 OK and healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["service"] == "backend"
    assert data["data"]["status"] == "healthy"
