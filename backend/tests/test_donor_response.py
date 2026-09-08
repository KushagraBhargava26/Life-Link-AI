# backend/tests/test_donor_response.py
# LifeLink AI — Donor Response & Coordination Test Suite
# Architecture Reference: ARCHITECTURE.md Section 33 & API.md Section 7

from __future__ import annotations

import datetime
import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


async def _create_authenticated_donor(
    client: AsyncClient,
    blood_type: str = "O+",
    city: str = "Mumbai",
    last_donation_date: str | None = None,
) -> tuple[dict, str, dict]:
    email = f"donor_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "SecurePassword123!"
    reg_resp = await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": pwd,
        "first_name": "Siddharth",
        "last_name": "Rao",
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
    headers = {"Authorization": f"Bearer {token}"}

    donor_payload = {
        "blood_type": blood_type,
        "city": city,
        "state": "Maharashtra",
        "pincode": "400001",
        "weight_kg": 72.0,
        "gender": "MALE",
        "is_available": True,
    }
    if last_donation_date:
        donor_payload["last_donation_date"] = last_donation_date

    p_resp = await client.post("/api/v1/donors", json=donor_payload, headers=headers)
    assert p_resp.status_code == 201
    donor = p_resp.json()["data"]

    return user, token, donor


async def _create_emergency_request(client: AsyncClient, blood_type: str = "O+") -> dict:
    payload = {
        "patient_name": "Test Trauma Patient",
        "patient_age": 42,
        "blood_type": blood_type,
        "units_required": 2,
        "urgency_level": "CRITICAL",
        "hospital_name": "KEM Hospital Trauma Center",
        "city": "Mumbai",
    }
    resp = await client.post("/api/v1/emergency", json=payload)
    assert resp.status_code == 201
    return resp.json()["data"]


@pytest.mark.asyncio
async def test_get_donor_opportunity_detail() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        _, token, _ = await _create_authenticated_donor(client, blood_type="O+")
        req = await _create_emergency_request(client, blood_type="O+")
        headers = {"Authorization": f"Bearer {token}"}

        resp = await client.get(f"/api/v1/donors/me/opportunities/{req['id']}", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["id"] == req["id"]
        assert data["data"]["blood_type"] == "O+"
        assert data["data"]["is_compatible"] is True
        assert data["data"]["donor_response"] is None


@pytest.mark.asyncio
async def test_donor_respond_accept_opportunity() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        _, token, _ = await _create_authenticated_donor(client, blood_type="O+")
        req = await _create_emergency_request(client, blood_type="O+")
        headers = {"Authorization": f"Bearer {token}"}

        # Respond ACCEPTED
        resp = await client.post(
            f"/api/v1/donors/me/opportunities/{req['id']}/respond",
            json={"status": "ACCEPTED", "notes": "Can reach in 30 minutes"},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["status"] == "ACCEPTED"
        assert data["data"]["notes"] == "Can reach in 30 minutes"

        # Verify opportunity details now include the response
        detail_resp = await client.get(f"/api/v1/donors/me/opportunities/{req['id']}", headers=headers)
        assert detail_resp.status_code == 200
        detail_data = detail_resp.json()["data"]
        assert detail_data["donor_response"] is not None
        assert detail_data["donor_response"]["status"] == "ACCEPTED"


@pytest.mark.asyncio
async def test_donor_respond_decline_opportunity() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        _, token, _ = await _create_authenticated_donor(client, blood_type="O+")
        req = await _create_emergency_request(client, blood_type="O+")
        headers = {"Authorization": f"Bearer {token}"}

        resp = await client.post(
            f"/api/v1/donors/me/opportunities/{req['id']}/respond",
            json={"status": "DECLINED", "notes": "Currently traveling"},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["status"] == "DECLINED"


@pytest.mark.asyncio
async def test_incompatible_donor_cannot_accept() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # A- donor cannot donate to O- patient
        _, token, _ = await _create_authenticated_donor(client, blood_type="A-")
        req = await _create_emergency_request(client, blood_type="O-")
        headers = {"Authorization": f"Bearer {token}"}

        resp = await client.post(
            f"/api/v1/donors/me/opportunities/{req['id']}/respond",
            json={"status": "ACCEPTED"},
            headers=headers,
        )
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_cooldown_donor_cannot_accept() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        recent_date = (datetime.date.today() - datetime.timedelta(days=15)).isoformat()
        _, token, _ = await _create_authenticated_donor(client, blood_type="O+")
        headers = {"Authorization": f"Bearer {token}"}

        # Update last_donation_date to 15 days ago
        up_resp = await client.put(
            "/api/v1/donors/me",
            json={"last_donation_date": recent_date},
            headers=headers,
        )
        assert up_resp.status_code == 200

        req = await _create_emergency_request(client, blood_type="O+")

        resp = await client.post(
            f"/api/v1/donors/me/opportunities/{req['id']}/respond",
            json={"status": "ACCEPTED"},
            headers=headers,
        )
        assert resp.status_code == 422
        assert "cooldown" in resp.json()["error"]["message"].lower()


