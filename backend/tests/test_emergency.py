# backend/tests/test_emergency.py
# LifeLink AI — Emergency Request API Tests
# Architecture Reference: ARCHITECTURE.md Section 35 (Testing Strategy)

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_create_valid_emergency_request() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "blood_type": "O-",
            "units_required": 2,
            "urgency_level": "CRITICAL",
            "hospital_name": "KEM Hospital",
            "city": "Mumbai",
            "patient_name": "Test Patient",
            "patient_age": 45,
            "notes": "Emergency ICU admission",
        }
        response = await client.post("/api/v1/emergency", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["blood_type"] == "O-"
        assert data["data"]["units_required"] == 2
        assert data["data"]["urgency_level"] == "CRITICAL"
        assert data["data"]["status"] == "PENDING"
        assert data["data"]["request_number"].startswith("EMR-")

        # Verify retrieval by request_number
        req_num = data["data"]["request_number"]
        get_res = await client.get(f"/api/v1/emergency/{req_num}")
        assert get_res.status_code == 200
        assert get_res.json()["data"]["request_number"] == req_num

        # Verify status check
        status_res = await client.get(f"/api/v1/emergency/{req_num}/status")
        assert status_res.status_code == 200
        assert status_res.json()["data"]["status"] == "PENDING"


@pytest.mark.asyncio
async def test_reject_invalid_blood_type() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "blood_type": "INVALID_TYPE",
            "units_required": 1,
            "urgency_level": "CRITICAL",
            "city": "Mumbai",
        }
        response = await client.post("/api/v1/emergency", json=payload)
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False


@pytest.mark.asyncio
async def test_reject_invalid_units() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Test units < 1
        response = await client.post("/api/v1/emergency", json={
            "blood_type": "A+",
            "units_required": 0,
            "urgency_level": "HIGH",
            "city": "Delhi",
        })
        assert response.status_code == 422

        # Test units > 20
        response2 = await client.post("/api/v1/emergency", json={
            "blood_type": "A+",
            "units_required": 25,
            "urgency_level": "HIGH",
            "city": "Delhi",
        })
        assert response2.status_code == 422


@pytest.mark.asyncio
async def test_reject_invalid_urgency() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/emergency", json={
            "blood_type": "B+",
            "units_required": 1,
            "urgency_level": "NOT_AN_URGENCY",
            "city": "Bengaluru",
        })
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_nonexistent_emergency() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/emergency/EMR-1999-9999")
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "EMERGENCY_NOT_FOUND"
