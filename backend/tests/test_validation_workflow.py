# backend/tests/test_validation_workflow.py
# LifeLink AI — Validation & Workflow Correction Test Suite
# Tests: Strict Name/Pincode/Blood Group/Age validation, facility-level hospital verification,
# emergency request creation, and role isolation.

from __future__ import annotations

import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


async def _create_user(client: AsyncClient, role: str, email_prefix: str = "user") -> tuple[dict, str]:
    email = f"{email_prefix}_{uuid.uuid4().hex[:6]}@lifelink.org"
    pwd = "SecurePass123!"
    reg = await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": pwd,
        "first_name": "John",
        "last_name": "Doe",
        "role": role,
    })
    assert reg.status_code == 201

    login = await client.post("/api/v1/auth/login", json={
        "email": email,
        "password": pwd,
    })
    assert login.status_code == 200
    token = login.json()["data"]["access_token"]
    user = login.json()["data"]["user"]
    return user, token


@pytest.mark.asyncio
async def test_name_validation_rejects_numeric_and_special_chars() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Invalid first name with numbers
        reg_fail1 = await client.post("/api/v1/auth/register", json={
            "email": f"test_fail_{uuid.uuid4().hex[:6]}@lifelink.org",
            "password": "SecurePass123!",
            "first_name": "John123",
            "last_name": "Doe",
            "role": "DONOR",
        })
        assert reg_fail1.status_code == 422

        # Invalid last name with symbols
        reg_fail2 = await client.post("/api/v1/auth/register", json={
            "email": f"test_fail_{uuid.uuid4().hex[:6]}@lifelink.org",
            "password": "SecurePass123!",
            "first_name": "John",
            "last_name": "Doe@@@",
            "role": "DONOR",
        })
        assert reg_fail2.status_code == 422


@pytest.mark.asyncio
async def test_emergency_intake_validation() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Invalid blood type
        resp_bad_blood = await client.post("/api/v1/emergency", json={
            "blood_type": "INVALID_TYPE",
            "units_required": 2,
            "urgency_level": "CRITICAL",
            "hospital_name": "General Hospital",
            "city": "Mumbai",
        })
        assert resp_bad_blood.status_code == 422

        # Invalid units required (0 or negative)
        resp_bad_units = await client.post("/api/v1/emergency", json={
            "blood_type": "O-",
            "units_required": 0,
            "urgency_level": "CRITICAL",
            "hospital_name": "General Hospital",
            "city": "Mumbai",
        })
        assert resp_bad_units.status_code == 422

        # Invalid patient name containing numbers
        resp_bad_name = await client.post("/api/v1/emergency", json={
            "blood_type": "O-",
            "units_required": 2,
            "urgency_level": "CRITICAL",
            "hospital_name": "General Hospital",
            "city": "Mumbai",
            "patient_name": "Patient999",
        })
        assert resp_bad_name.status_code == 422

        # Valid emergency request
        resp_valid = await client.post("/api/v1/emergency", json={
            "blood_type": "O-",
            "units_required": 2,
            "urgency_level": "CRITICAL",
            "hospital_name": "Lilavati Hospital",
            "city": "Mumbai",
            "patient_name": "Priya Sharma",
            "patient_age": 34,
        })
        assert resp_valid.status_code == 201
        data = resp_valid.json()["data"]
        assert data["blood_type"] == "O-"
        assert data["status"] in {"PENDING", "MATCHING"}


@pytest.mark.asyncio
async def test_donor_pincode_and_weight_validation() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        user, token = await _create_user(client, "DONOR", "donor_val")
        headers = {"Authorization": f"Bearer {token}"}

        # Invalid weight (< 45 kg)
        resp_underweight = await client.post("/api/v1/donors", headers=headers, json={
            "blood_type": "A+",
            "city": "Mumbai",
            "weight_kg": 40.0,
        })
        assert resp_underweight.status_code == 422

        # Invalid pincode (alphabetic)
        resp_bad_pincode = await client.post("/api/v1/donors", headers=headers, json={
            "blood_type": "A+",
            "city": "Mumbai",
            "weight_kg": 65.0,
            "pincode": "ABCD12",
        })
        assert resp_bad_pincode.status_code == 422

        # Valid donor profile
        resp_valid = await client.post("/api/v1/donors", headers=headers, json={
            "blood_type": "A+",
            "city": "Mumbai",
            "state": "Maharashtra",
            "pincode": "400001",
            "weight_kg": 65.0,
            "gender": "MALE",
        })
        assert resp_valid.status_code == 201


@pytest.mark.asyncio
async def test_facility_level_hospital_verification_and_request_creation() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create hospital staff user
        hosp_user, hosp_token = await _create_user(client, "HOSPITAL_ADMIN", "hosp_wf")
        hosp_headers = {"Authorization": f"Bearer {hosp_token}"}

        # Create hospital profile
        hosp_resp = await client.post("/api/v1/hospitals", headers=hosp_headers, json={
            "name": f"City Care {uuid.uuid4().hex[:4]}",
            "type": "PRIVATE",
            "address_line": "456 Hospital Road",
            "city": "Mumbai",
            "state": "Maharashtra",
            "pincode": "400002",
            "phone": "+912226751000",
        })
        assert hosp_resp.status_code == 201
        hosp_data = hosp_resp.json()["data"]
        assert hosp_data["is_verified"] is False

        # Hospital can create an emergency request directly
        req_resp = await client.post("/api/v1/hospitals/me/requests", headers=hosp_headers, json={
            "blood_type": "B+",
            "units_required": 3,
            "urgency_level": "CRITICAL",
        })
        assert req_resp.status_code == 201
        req_data = req_resp.json()["data"]
        assert req_data["blood_type"] == "B+"
        assert req_data["status"] == "PENDING"
        assert req_data["request_number"].startswith("EMR-")
