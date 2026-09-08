# backend/tests/test_hospital.py
# LifeLink AI — Hospital Module Test Suite
# Architecture Reference: ARCHITECTURE.md Section 27, 30; API.md Section 8

from __future__ import annotations

import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


async def _create_hospital_user(client: AsyncClient, email: str | None = None) -> tuple[dict, str]:
    if not email:
        email = f"hosp_admin_{uuid.uuid4().hex[:8]}@example.com"
    pwd = "SecurePassword123!"
    reg_resp = await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": pwd,
        "first_name": "Dr. Ananya",
        "last_name": "Roy",
        "role": "HOSPITAL_ADMIN",
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
async def test_create_hospital_profile() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        user, token = await _create_hospital_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        reg_num = f"MH-HOSP-{uuid.uuid4().hex[:6].upper()}"
        payload = {
            "name": "Lilavati Hospital & Research Centre",
            "registration_number": reg_num,
            "type": "PRIVATE",
            "address_line": "A-791, Bandra Reclamation, Bandra West",
            "city": "Mumbai",
            "state": "Maharashtra",
            "pincode": "400050",
            "phone": "+91 22 2675 1000",
            "email": "trauma@lilavati.org",
            "bed_count": 314,
            "has_blood_bank": True,
        }
        res = await client.post("/api/v1/hospitals", json=payload, headers=headers)
        assert res.status_code == 201
        data = res.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Lilavati Hospital & Research Centre"
        assert data["data"]["registration_number"] == reg_num
        assert data["data"]["city"] == "Mumbai"
        assert data["data"]["has_blood_bank"] is True
        assert data["data"]["is_active"] is True


@pytest.mark.asyncio
async def test_get_my_hospital_profile() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        user, token = await _create_hospital_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        payload = {
            "name": "Fortis Memorial Hospital",
            "type": "PRIVATE",
            "address_line": "Sector 44, Opposite HUDA City Centre",
            "city": "Gurugram",
            "state": "Haryana",
            "pincode": "122002",
            "phone": "+91 124 4921021",
        }
        create_res = await client.post("/api/v1/hospitals", json=payload, headers=headers)
        assert create_res.status_code == 201

        get_res = await client.get("/api/v1/hospitals/me", headers=headers)
        assert get_res.status_code == 200
        get_data = get_res.json()
        assert get_data["success"] is True
        assert get_data["data"]["name"] == "Fortis Memorial Hospital"
        assert get_data["data"]["city"] == "Gurugram"


@pytest.mark.asyncio
async def test_update_my_hospital_profile() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        user, token = await _create_hospital_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        payload = {
            "name": "Apollo Gleneagles Hospital",
            "type": "SPECIALTY",
            "address_line": "58 Canal Circular Road",
            "city": "Kolkata",
            "state": "West Bengal",
            "pincode": "700054",
            "phone": "+91 33 2320 3040",
            "bed_count": 500,
        }
        await client.post("/api/v1/hospitals", json=payload, headers=headers)

        update_payload = {
            "bed_count": 650,
            "has_blood_bank": True,
            "phone": "+91 33 2320 9999",
        }
        update_res = await client.put("/api/v1/hospitals/me", json=update_payload, headers=headers)
        assert update_res.status_code == 200
        update_data = update_res.json()
        assert update_data["data"]["bed_count"] == 650
        assert update_data["data"]["has_blood_bank"] is True
        assert update_data["data"]["phone"] == "+91 33 2320 9999"


@pytest.mark.asyncio
async def test_reject_duplicate_registration_number() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        _, token1 = await _create_hospital_user(client)
        _, token2 = await _create_hospital_user(client)

        reg_num = f"DUP-REG-{uuid.uuid4().hex[:6]}"
        payload = {
            "name": "Hospital Alpha",
            "registration_number": reg_num,
            "type": "TRUST",
            "address_line": "Road 1",
            "city": "Delhi",
            "state": "Delhi",
            "pincode": "110001",
            "phone": "9876543210",
        }
        res1 = await client.post("/api/v1/hospitals", json=payload, headers={"Authorization": f"Bearer {token1}"})
        assert res1.status_code == 201

        payload["name"] = "Hospital Beta"
        res2 = await client.post("/api/v1/hospitals", json=payload, headers={"Authorization": f"Bearer {token2}"})
        assert res2.status_code == 409


@pytest.mark.asyncio
async def test_hospital_dashboard_and_emergency_requests() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        user, token = await _create_hospital_user(client)
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Register hospital
        payload = {
            "name": "Tata Memorial Centre",
            "type": "GOVERNMENT",
            "address_line": "Dr. E Borges Road, Parel",
            "city": "Mumbai",
            "state": "Maharashtra",
            "pincode": "400012",
            "phone": "+91 22 2417 7000",
            "has_blood_bank": True,
        }
        await client.post("/api/v1/hospitals", json=payload, headers=headers)

        # 2. Check empty dashboard
        dash_res = await client.get("/api/v1/hospitals/me/dashboard", headers=headers)
        assert dash_res.status_code == 200
        dash_data = dash_res.json()["data"]
        assert dash_data["active_requests_count"] == 0
        assert dash_data["hospital"]["name"] == "Tata Memorial Centre"

        # 3. Create hospital emergency requisition
        req_payload = {
            "blood_type": "O-",
            "units_required": 3,
            "urgency_level": "CRITICAL",
            "patient_age": 45,
            "notes": "Emergency ICU cardiac surgery requisition",
        }
        req_res = await client.post("/api/v1/hospitals/me/requests", json=req_payload, headers=headers)
        assert req_res.status_code == 201
        req_data = req_res.json()["data"]
        assert req_data["blood_type"] == "O-"
        assert req_data["units_required"] == 3
        assert req_data["hospital_name"] == "Tata Memorial Centre"
        assert req_data["status"] == "PENDING"
        assert req_data["request_number"].startswith("EMR-")

        # 4. Verify request appears in hospital requests list
        list_res = await client.get("/api/v1/hospitals/me/requests", headers=headers)
        assert list_res.status_code == 200
        items = list_res.json()["data"]["items"]
        assert len(items) >= 1
        assert items[0]["request_number"] == req_data["request_number"]

        # 5. Verify dashboard shows active request
        dash_res2 = await client.get("/api/v1/hospitals/me/dashboard", headers=headers)
        assert dash_res2.status_code == 200
        assert dash_res2.json()["data"]["active_requests_count"] >= 1


@pytest.mark.asyncio
async def test_unauthenticated_hospital_access() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/v1/hospitals/me")
        assert res.status_code == 401
