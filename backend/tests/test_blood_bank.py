# backend/tests/test_blood_bank.py
# LifeLink AI — Blood Bank Module Test Suite
# Architecture Reference: ARCHITECTURE.md Section 27, 30; API.md Section 9

from __future__ import annotations

import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


async def _create_bb_user(client: AsyncClient, email: str | None = None) -> tuple[dict, str]:
    if not email:
        email = f"bb_manager_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "SecurePassword123!"
    reg_resp = await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": pwd,
        "first_name": "Suresh",
        "last_name": "Patel",
        "role": "BLOOD_BANK_MANAGER",
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
async def test_create_blood_bank_profile() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        user, token = await _create_bb_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        lic_num = f"MH-BB-{uuid.uuid4().hex[:6].upper()}"
        payload = {
            "name": "Red Cross Central Blood Bank",
            "license_number": lic_num,
            "address_line": "141 Shahid Bhagat Singh Road, Fort",
            "city": "Mumbai",
            "state": "Maharashtra",
            "pincode": "400001",
            "phone": "+91 22 2266 1234",
            "email": "mumbai@redcrossblood.org",
            "operating_hours": "24/7",
            "is_24_hours": True,
            "accepts_walk_in": True,
        }
        res = await client.post("/api/v1/blood-banks", json=payload, headers=headers)
        assert res.status_code == 201
        data = res.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Red Cross Central Blood Bank"
        assert data["data"]["license_number"] == lic_num
        assert data["data"]["city"] == "Mumbai"
        assert data["data"]["is_24_hours"] is True
        assert data["data"]["accepts_walk_in"] is True


@pytest.mark.asyncio
async def test_get_my_blood_bank_profile() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        user, token = await _create_bb_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        payload = {
            "name": "Rotary Blood Bank",
            "address_line": "56 Tughlakabad Institutional Area",
            "city": "New Delhi",
            "state": "Delhi",
            "pincode": "110062",
            "phone": "+91 11 2995 5995",
        }
        create_res = await client.post("/api/v1/blood-banks", json=payload, headers=headers)
        assert create_res.status_code == 201

        get_res = await client.get("/api/v1/blood-banks/me", headers=headers)
        assert get_res.status_code == 200
        get_data = get_res.json()["data"]
        assert get_data["name"] == "Rotary Blood Bank"
        assert get_data["city"] == "New Delhi"


@pytest.mark.asyncio
async def test_update_my_blood_bank_profile() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        user, token = await _create_bb_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        payload = {
            "name": "Prathama Blood Centre",
            "address_line": "Vasna Barrage Road",
            "city": "Ahmedabad",
            "state": "Gujarat",
            "pincode": "380007",
            "phone": "+91 79 2660 0101",
            "is_24_hours": False,
        }
        await client.post("/api/v1/blood-banks", json=payload, headers=headers)

        update_payload = {
            "is_24_hours": True,
            "operating_hours": "Round the Clock 24/7",
            "phone": "+91 79 2660 9999",
        }
        update_res = await client.put("/api/v1/blood-banks/me", json=update_payload, headers=headers)
        assert update_res.status_code == 200
        data = update_res.json()["data"]
        assert data["is_24_hours"] is True
        assert data["operating_hours"] == "Round the Clock 24/7"
        assert data["phone"] == "+91 79 2660 9999"


@pytest.mark.asyncio
async def test_reject_duplicate_license_number() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        _, token1 = await _create_bb_user(client)
        _, token2 = await _create_bb_user(client)

        lic_num = f"DUP-LIC-{uuid.uuid4().hex[:6]}"
        payload = {
            "name": "Blood Bank Alpha",
            "license_number": lic_num,
            "address_line": "100 Park Street",
            "city": "Kolkata",
            "state": "West Bengal",
            "pincode": "700016",
            "phone": "+91 33 2222 1111",
        }
        res1 = await client.post("/api/v1/blood-banks", json=payload, headers={"Authorization": f"Bearer {token1}"})
        assert res1.status_code == 201

        payload["name"] = "Blood Bank Beta"
        res2 = await client.post("/api/v1/blood-banks", json=payload, headers={"Authorization": f"Bearer {token2}"})
        assert res2.status_code == 409


@pytest.mark.asyncio
async def test_blood_bank_dashboard_and_demand_visibility() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        user, token = await _create_bb_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Create Blood Bank in Mumbai
        bb_payload = {
            "name": "KEM Hospital Blood Bank",
            "address_line": "Acharya Donde Marg, Parel",
            "city": "Mumbai",
            "state": "Maharashtra",
            "pincode": "400012",
            "phone": "+91 22 2413 6051",
            "is_24_hours": True,
        }
        await client.post("/api/v1/blood-banks", json=bb_payload, headers=headers)

        # 2. Check dashboard
        dash_res = await client.get("/api/v1/blood-banks/me/dashboard", headers=headers)
        assert dash_res.status_code == 200
        dash_data = dash_res.json()["data"]
        assert dash_data["blood_bank"]["name"] == "KEM Hospital Blood Bank"
        assert dash_data["is_operational"] is True
        assert isinstance(dash_data["active_emergency_demand_count"], int)

        # 3. Check demand feed
        demand_res = await client.get("/api/v1/blood-banks/me/demand", headers=headers)
        assert demand_res.status_code == 200
        demand_data = demand_res.json()["data"]
        assert "items" in demand_data
        assert "total" in demand_data


@pytest.mark.asyncio
async def test_unauthenticated_blood_bank_access() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/v1/blood-banks/me")
        assert res.status_code == 401
