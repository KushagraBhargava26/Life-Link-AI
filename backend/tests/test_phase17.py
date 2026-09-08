# backend/tests/test_phase17.py
# LifeLink AI — Phase 1.7 Test Suite
# Tests: Admin verifications, Donor Dashboard endpoint, Auth Profile update

from __future__ import annotations

import uuid
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


async def _create_user_with_role(client: AsyncClient, role: str) -> tuple[dict, str]:
    email = f"user_{role.lower()}_{uuid.uuid4().hex[:6]}@lifelink.org"
    pwd = "SecurePass123!"
    reg = await client.post("/api/v1/auth/register", json={
        "email": email,
        "password": pwd,
        "first_name": "Test",
        "last_name": "User",
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
async def test_auth_profile_update() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        user, token = await _create_user_with_role(client, "DONOR")
        headers = {"Authorization": f"Bearer {token}"}

        # Update first_name and phone
        patch_resp = await client.patch("/api/v1/auth/me", headers=headers, json={
            "first_name": "UpdatedName",
            "phone": "+919876543210",
        })
        assert patch_resp.status_code == 200
        data = patch_resp.json()["data"]
        assert data["first_name"] == "UpdatedName"
        assert data["phone"] == "+919876543210"


@pytest.mark.asyncio
async def test_donor_dashboard_endpoint() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        user, token = await _create_user_with_role(client, "DONOR")
        headers = {"Authorization": f"Bearer {token}"}

        # Query dashboard before creating donor profile
        dash1 = await client.get("/api/v1/donors/me/dashboard", headers=headers)
        assert dash1.status_code == 200
        assert dash1.json()["data"]["has_profile"] is False

        # Create donor profile
        create_resp = await client.post("/api/v1/donors", headers=headers, json={
            "blood_type": "O-",
            "city": "Mumbai",
            "is_available": True,
        })
        assert create_resp.status_code == 201

        # Query dashboard after profile creation
        dash2 = await client.get("/api/v1/donors/me/dashboard", headers=headers)
        assert dash2.status_code == 200
        d_data = dash2.json()["data"]
        assert d_data["has_profile"] is True
        assert d_data["is_available"] is True
        assert d_data["is_eligible"] is True
        assert isinstance(d_data["compatible_opportunities"], list)


@pytest.mark.asyncio
async def test_admin_verification_workflow() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create super admin
        admin_user, admin_token = await _create_user_with_role(client, "SUPER_ADMIN")
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # Create hospital
        hosp_user, hosp_token = await _create_user_with_role(client, "HOSPITAL_ADMIN")
        hosp_headers = {"Authorization": f"Bearer {hosp_token}"}
        hosp_resp = await client.post("/api/v1/hospitals", headers=hosp_headers, json={
            "name": f"City Trauma Care {uuid.uuid4().hex[:4]}",
            "type": "PRIVATE",
            "address_line": "123 Medical Blvd",
            "city": "Mumbai",
            "state": "Maharashtra",
            "pincode": "400001",
            "phone": "+919876543210",
        })
        assert hosp_resp.status_code == 201
        hosp_id = hosp_resp.json()["data"]["id"]

        # Admin gets pending verifications
        pending_resp = await client.get("/api/v1/admin/verifications/pending", headers=admin_headers)
        assert pending_resp.status_code == 200
        pending_data = pending_resp.json()["data"]
        assert pending_data["total_pending"] >= 1
        found_hosp = any(h["id"] == hosp_id for h in pending_data["hospitals"])
        assert found_hosp is True

        # Admin verifies hospital
        verify_resp = await client.patch(
            f"/api/v1/admin/hospitals/{hosp_id}/verify",
            headers=admin_headers,
            json={"is_verified": True},
        )
        assert verify_resp.status_code == 200
        assert verify_resp.json()["data"]["is_verified"] is True

        # Non-admin cannot access admin endpoints (RBAC)
        forbidden_resp = await client.get("/api/v1/admin/verifications/pending", headers=hosp_headers)
        assert forbidden_resp.status_code == 403
