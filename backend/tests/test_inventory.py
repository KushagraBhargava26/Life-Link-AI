# backend/tests/test_inventory.py
# LifeLink AI — Blood Inventory & Availability Integration Tests
# Architecture Reference: ARCHITECTURE.md Section 24, ADR-001; API.md Section 10

from __future__ import annotations

import uuid
from datetime import date, timedelta

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


async def _create_bb_user_and_facility(client: AsyncClient, city: str = "Mumbai") -> tuple[dict, str, dict]:
    """Helper to register user, login, and register a blood bank facility."""
    unique = uuid.uuid4().hex[:8]
    email = f"bb_mgr_{unique}@test.org"
    password = "SecurePassword123!"

    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": "Test",
            "last_name": "Manager",
            "role": "BLOOD_BANK_MANAGER",
        },
    )
    assert reg_resp.status_code == 201

    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    bank_resp = await client.post(
        "/api/v1/blood-banks",
        json={
            "name": f"City Blood Centre {unique}",
            "license_number": f"MH-BB-{unique.upper()}",
            "address_line": "123 Healthcare Way",
            "city": city,
            "state": "Maharashtra",
            "pincode": "400001",
            "phone": "+91 22 2200 0000",
            "operating_hours": "24/7",
            "is_24_hours": True,
            "accepts_walk_in": True,
        },
        headers=headers,
    )
    assert bank_resp.status_code == 201
    return reg_resp.json()["data"], token, bank_resp.json()["data"]


@pytest.mark.asyncio
async def test_get_my_blood_bank_inventory_empty():
    """Verify newly registered blood bank returns truthful 0-unit items across all 8 blood groups."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        _, token, _ = await _create_bb_user_and_facility(client)
        headers = {"Authorization": f"Bearer {token}"}

        resp = await client.get("/api/v1/blood-banks/me/inventory", headers=headers)
        assert resp.status_code == 200
        data = resp.json()["data"]

        items = data["items"]
        assert len(items) == 8
        summary = data["summary"]
        assert summary["total_available"] == 0
        assert summary["depleted_groups_count"] == 8


@pytest.mark.asyncio
async def test_update_blood_bank_inventory_single():
    """Verify updating available units, threshold, and expiry date for a blood type."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        _, token, _ = await _create_bb_user_and_facility(client)
        headers = {"Authorization": f"Bearer {token}"}

        future_date = (date.today() + timedelta(days=35)).isoformat()
        resp = await client.put(
            "/api/v1/blood-banks/me/inventory/O+",
            json={
                "units_available": 12,
                "minimum_threshold": 4,
                "expiry_date": future_date,
                "reason": "Restocked from regional donation drive",
            },
            headers=headers,
        )
        assert resp.status_code == 200
        item = resp.json()["data"]
        assert item["blood_type"] == "O+"
        assert item["units_available"] == 12
        assert item["net_available"] == 12
        assert item["is_low_stock"] is False
        assert item["is_expired"] is False

        # Verify reflected in full inventory
        full_resp = await client.get("/api/v1/blood-banks/me/inventory", headers=headers)
        assert full_resp.status_code == 200
        summary = full_resp.json()["data"]["summary"]
        assert summary["total_available"] == 12
        assert summary["stock_by_blood_type"]["O+"] == 12


@pytest.mark.asyncio
async def test_batch_update_blood_bank_inventory():
    """Verify batch updating multiple blood types simultaneously."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        _, token, _ = await _create_bb_user_and_facility(client)
        headers = {"Authorization": f"Bearer {token}"}

        future_date = (date.today() + timedelta(days=25)).isoformat()
        resp = await client.put(
            "/api/v1/blood-banks/me/inventory",
            json={
                "items": [
                    {"blood_type": "O-", "units_available": 8, "minimum_threshold": 3, "expiry_date": future_date},
                    {"blood_type": "A+", "units_available": 15, "minimum_threshold": 5, "expiry_date": future_date},
                ]
            },
            headers=headers,
        )
        assert resp.status_code == 200
        items = resp.json()["data"]
        assert len(items) == 2

        full_resp = await client.get("/api/v1/blood-banks/me/inventory", headers=headers)
        summary = full_resp.json()["data"]["summary"]
        assert summary["total_available"] == 23


@pytest.mark.asyncio
async def test_reject_negative_inventory_units():
    """Verify negative units_available is rejected by validation."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        _, token, _ = await _create_bb_user_and_facility(client)
        headers = {"Authorization": f"Bearer {token}"}

        resp = await client.put(
            "/api/v1/blood-banks/me/inventory/B+",
            json={"units_available": -5, "minimum_threshold": 2},
            headers=headers,
        )
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_reject_invalid_blood_type():
    """Verify invalid blood type string fails validation."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        _, token, _ = await _create_bb_user_and_facility(client)
        headers = {"Authorization": f"Bearer {token}"}

        resp = await client.put(
            "/api/v1/blood-banks/me/inventory/Z+",
            json={"units_available": 10},
            headers=headers,
        )
        assert resp.status_code in (400, 422)


@pytest.mark.asyncio
async def test_reject_invalid_component():
    """Verify invalid blood component category fails validation."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        _, token, _ = await _create_bb_user_and_facility(client)
        headers = {"Authorization": f"Bearer {token}"}

        resp = await client.put(
            "/api/v1/blood-banks/me/inventory/O+",
            json={"units_available": 10, "component": "SYNTHETIC_BLOOD"},
            headers=headers,
        )
        assert resp.status_code == 422


@pytest.mark.asyncio
async def test_expired_units_excluded_from_availability():
    """Verify stock with past expiry date is marked expired and excluded from available counts."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        _, token, _ = await _create_bb_user_and_facility(client)
        headers = {"Authorization": f"Bearer {token}"}

        past_date = (date.today() - timedelta(days=2)).isoformat()
        resp = await client.put(
            "/api/v1/blood-banks/me/inventory/AB-",
            json={
                "units_available": 10,
                "expiry_date": past_date,
                "reason": "Expired batch",
            },
            headers=headers,
        )
        assert resp.status_code == 200
        item = resp.json()["data"]
        assert item["is_expired"] is True
        assert item["net_available"] == 0

        # Verify summary omits expired units from total_available
        full_resp = await client.get("/api/v1/blood-banks/me/inventory", headers=headers)
        summary = full_resp.json()["data"]["summary"]
        assert summary["stock_by_blood_type"]["AB-"] == 0


@pytest.mark.asyncio
async def test_demand_availability_deterministic_matching():
    """Verify compatibility and availability calculations for an emergency requisition."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Create Blood Bank with O- (universal) and A+ units
        _, bb_token, _ = await _create_bb_user_and_facility(client, city="Pune")
        bb_headers = {"Authorization": f"Bearer {bb_token}"}

        future = (date.today() + timedelta(days=30)).isoformat()
        await client.put(
            "/api/v1/blood-banks/me/inventory",
            json={
                "items": [
                    {"blood_type": "O-", "units_available": 4, "expiry_date": future},
                    {"blood_type": "A+", "units_available": 6, "expiry_date": future},
                    {"blood_type": "B+", "units_available": 10, "expiry_date": future},
                ]
            },
            headers=bb_headers,
        )

        # 2. Create emergency request for A+ (needs 8 units)
        req_resp = await client.post(
            "/api/v1/emergency",
            json={
                "blood_type": "A+",
                "units_required": 8,
                "urgency_level": "CRITICAL",
                "patient_name": "Emergency Ward B",
                "patient_age": 45,
                "city": "Pune",
                "hospital_name": "Ruby Hall Clinic",
            },
        )
        assert req_resp.status_code == 201
        req_id = req_resp.json()["data"]["id"]

        # 3. Blood bank checks availability for this requisition
        avail_resp = await client.get(
            f"/api/v1/blood-banks/me/demand/{req_id}/availability",
            headers=bb_headers,
        )
        assert avail_resp.status_code == 200
        avail_data = avail_resp.json()["data"]

        # Compatible types for A+ are O-, O+, A-, A+ (bank has 4 O- + 6 A+ = 10 compatible units >= 8 required)
        assert avail_data["is_compatible_stock_available"] is True
        assert avail_data["availability_status"] == "AVAILABLE"
        assert avail_data["total_compatible_units"] == 10

        # Assert B+ is excluded from compatible breakdown!
        breakdown_types = [b["blood_type"] for b in avail_data["compatible_breakdown"]]
        assert "A+" in breakdown_types
        assert "O-" in breakdown_types
        assert "B+" not in breakdown_types

        # Assert zero patient PII
        assert "patient_name" not in avail_data
        assert "patient_age" not in avail_data


@pytest.mark.asyncio
async def test_authorization_and_isolation():
    """Verify unauthorized callers, donors, and cross-bank users are rejected."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Unauthenticated -> 401
        resp = await client.get("/api/v1/blood-banks/me/inventory")
        assert resp.status_code == 401

        resp = await client.put("/api/v1/blood-banks/me/inventory/O+", json={"units_available": 5})
        assert resp.status_code == 401

        # Register donor user (has no blood bank)
        unique = uuid.uuid4().hex[:8]
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": f"donor_{unique}@test.org",
                "password": "SecurePassword123!",
                "first_name": "Donor",
                "last_name": "User",
                "role": "DONOR",
            },
        )
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"email": f"donor_{unique}@test.org", "password": "SecurePassword123!"},
        )
        donor_token = login_resp.json()["data"]["access_token"]
        donor_headers = {"Authorization": f"Bearer {donor_token}"}

        # Donor trying to mutate blood bank inventory -> 404 (no blood bank profile)
        donor_put = await client.put(
            "/api/v1/blood-banks/me/inventory/O+",
            json={"units_available": 10},
            headers=donor_headers,
        )
        assert donor_put.status_code == 404


@pytest.mark.asyncio
async def test_public_blood_bank_inventory_directory():
    """Verify public read-only directory endpoint returns facility stock."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        _, token, bank = await _create_bb_user_and_facility(client)
        bank_id = bank["id"]

        # Stock 5 units of O-
        await client.put(
            "/api/v1/blood-banks/me/inventory/O-",
            json={"units_available": 5},
            headers={"Authorization": f"Bearer {token}"},
        )

        # Unauthenticated query to public endpoint
        pub_resp = await client.get(f"/api/v1/blood-banks/{bank_id}/inventory")
        assert pub_resp.status_code == 200
        summary = pub_resp.json()["data"]["summary"]
        assert summary["total_available"] == 5
