# backend/tests/test_donor.py
# LifeLink AI — Donor Profile Test Suite
# Architecture Reference: ARCHITECTURE.md Section 33 & Section 35

from __future__ import annotations

import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


async def _create_authenticated_user(client: AsyncClient, email: str | None = None) -> tuple[dict, str]:
    if not email:
        email = f"donor_test_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "SecurePassword123!"
    reg_resp = await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": pwd,
        "first_name": "Rohan",
        "last_name": "Verma",
        "role": "DONOR",
    })
    assert reg_resp.status_code == 201

    login_resp = await client.post("/api/v1/auth/login", json={
        "email": email,
        "password": pwd,
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["data"]["access_token"]
    user = login_resp.json()["data"]["user"]
    return user, token


@pytest.mark.asyncio
async def test_create_donor_profile() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        user, token = await _create_authenticated_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        payload = {
            "blood_type": "O-",
            "city": "Mumbai",
            "state": "Maharashtra",
            "pincode": "400050",
            "weight_kg": 68.5,
            "gender": "MALE",
            "is_available": True,
        }
        response = await client.post("/api/v1/donors", json=payload, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["blood_type"] == "O-"
        assert data["data"]["city"] == "Mumbai"
        assert data["data"]["is_available"] is True
        assert data["data"]["is_eligible"] is True
        assert data["data"]["user_id"] == user["id"]


@pytest.mark.asyncio
async def test_get_my_donor_profile() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        user, token = await _create_authenticated_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        # Create
        await client.post("/api/v1/donors", json={
            "blood_type": "A+",
            "city": "Pune",
            "weight_kg": 72.0,
            "is_available": True,
        }, headers=headers)

        # Get me
        response = await client.get("/api/v1/donors/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["blood_type"] == "A+"
        assert data["data"]["city"] == "Pune"


@pytest.mark.asyncio
async def test_update_donor_profile() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        user, token = await _create_authenticated_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        # Create
        await client.post("/api/v1/donors", json={
            "blood_type": "B+",
            "city": "Nagpur",
            "weight_kg": 60.0,
            "is_available": True,
        }, headers=headers)

        # Update
        update_resp = await client.put("/api/v1/donors/me", json={
            "city": "Thane",
            "weight_kg": 62.5,
        }, headers=headers)
        assert update_resp.status_code == 200
        data = update_resp.json()
        assert data["success"] is True
        assert data["data"]["city"] == "Thane"
        assert data["data"]["weight_kg"] == 62.5


@pytest.mark.asyncio
async def test_toggle_donor_availability() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        user, token = await _create_authenticated_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        # Create
        await client.post("/api/v1/donors", json={
            "blood_type": "AB+",
            "city": "Delhi",
            "weight_kg": 65.0,
            "is_available": True,
        }, headers=headers)

        # Toggle to False
        patch_resp = await client.patch("/api/v1/donors/me/availability", json={
            "is_available": False,
        }, headers=headers)
        assert patch_resp.status_code == 200
        assert patch_resp.json()["data"]["is_available"] is False

        # Toggle back to True
        patch_resp2 = await client.patch("/api/v1/donors/me/availability", json={
            "is_available": True,
        }, headers=headers)
        assert patch_resp2.status_code == 200
        assert patch_resp2.json()["data"]["is_available"] is True


@pytest.mark.asyncio
async def test_unauthenticated_donor_access() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/donors/me")
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "AUTH_TOKEN_MISSING"


@pytest.mark.asyncio
async def test_reject_underweight_donor() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        user, token = await _create_authenticated_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.post("/api/v1/donors", json={
            "blood_type": "O+",
            "city": "Mumbai",
            "weight_kg": 40.0,  # Below 45kg requirement
        }, headers=headers)
        assert response.status_code == 422
        assert response.json()["success"] is False


@pytest.mark.asyncio
async def test_reject_invalid_blood_type() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        user, token = await _create_authenticated_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.post("/api/v1/donors", json={
            "blood_type": "INVALID_TYPE",
            "city": "Mumbai",
        }, headers=headers)
        assert response.status_code == 422
        assert response.json()["success"] is False
