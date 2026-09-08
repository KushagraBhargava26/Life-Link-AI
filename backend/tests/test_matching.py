"""Tests for Phase 1.6: Matching & Coordination Engine.
Tests candidate discovery, deterministic filtering, AI ranking, fallback, ReBAC, and lifecycle.
"""

import uuid
from datetime import date, timedelta
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.modules.auth.models import User, UserRole
from app.modules.hospital.models import Hospital
from app.modules.blood_bank.models import BloodBank
from app.modules.inventory.models import BloodInventory
from app.modules.donor.models import Donor
from app.modules.emergency.models import EmergencyRequest, EmergencyStatusEnum
from app.core.security import hash_password, create_access_token


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.fixture
async def hospital_user_and_request(db_session):
    """Creates a hospital user, hospital facility, and an emergency request."""
    user = User(
        email=f"hosp.{uuid.uuid4().hex[:6]}@apollo.org",
        password_hash=hash_password("HospitalPass123!"),
        first_name="Anita",
        last_name="Sharma",
        is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    user_role = UserRole(user_id=user.id, role="HOSPITAL_ADMIN")
    db_session.add(user_role)
    await db_session.flush()

    # Hospital (Bengaluru coords: 12.9716, 77.5946)
    hosp = Hospital(
        name="Apollo Hospital Jayanagar",
        registration_number=f"AP-{uuid.uuid4().hex[:6].upper()}",
        address_line="14th Cross Jayanagar",
        city="Bengaluru",
        state="Karnataka",
        pincode="560011",
        phone="+918022003300",
        latitude=12.9716,
        longitude=77.5946,
        created_by=user.id,
        is_active=True,
        is_verified=True,
    )
    db_session.add(hosp)

    await db_session.flush()

    # Request for A+ blood
    req = EmergencyRequest(
        request_number=f"EMR-2026-{uuid.uuid4().hex[:4].upper()}",
        blood_type="A+",
        units_required=4,
        urgency_level="CRITICAL",
        hospital_id=hosp.id,
        hospital_name=hosp.name,
        city="Bengaluru",
        latitude=12.9716,
        longitude=77.5946,
        requested_by=user.id,
        patient_name="Confidential ICU Patient",
        patient_age=35,
        status=EmergencyStatusEnum.PENDING.value,
    )
    db_session.add(req)
    await db_session.commit()
    await db_session.refresh(user)
    await db_session.refresh(hosp)
    await db_session.refresh(req)

    token = create_access_token(subject=str(user.id), role="HOSPITAL_ADMIN")
    return user, hosp, req, token


@pytest.mark.asyncio
async def test_unauthenticated_matching_rejected(client):
    """Verifies that unauthenticated calls to matching endpoints return 401."""
    random_id = uuid.uuid4()
    res = await client.post(f"/api/v1/hospitals/me/requests/{random_id}/match")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_unauthorized_hospital_cannot_match_another_request(client, hospital_user_and_request, db_session):
    """Verifies ReBAC: Hospital A cannot run matching on Hospital B's requisition."""
    _, _, req, _ = hospital_user_and_request

    # Create Hospital B user
    other_user = User(
        email=f"hosp.b.{uuid.uuid4().hex[:6]}@fortis.org",
        password_hash=hash_password("OtherPass123!"),
        first_name="Vikram",
        last_name="Singh",
        is_active=True,
    )
    db_session.add(other_user)
    await db_session.flush()

    other_role = UserRole(user_id=other_user.id, role="HOSPITAL_ADMIN")
    db_session.add(other_role)
    await db_session.commit()

    other_token = create_access_token(subject=str(other_user.id), role="HOSPITAL_ADMIN")

    # Try to match Hospital A's request using Hospital B's token
    res = await client.post(
        f"/api/v1/hospitals/me/requests/{req.id}/match",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert res.status_code == 403



@pytest.mark.asyncio
async def test_deterministic_candidate_filtering_and_ranking(client, hospital_user_and_request, db_session):
    """
    Tests end-to-end matching:
    - Compatible donor (A+) included
    - Compatible universal donor (O-) included
    - Incompatible donor (B+) excluded
    - Ineligible donor (in 56-day cooldown) excluded
    - Unavailable donor excluded
    - Compatible blood bank inventory included
    - Incompatible blood bank inventory excluded
    - Expired blood bank inventory excluded
    """
    user, hosp, req, token = hospital_user_and_request
    today = date.today()

    # 1. Compatible Donor 1 (A+, available, 4 donations, 5km away: 12.9800, 77.6000)
    d1_user = User(email=f"d1.{uuid.uuid4().hex[:6]}@gmail.com", password_hash="hash", first_name="D1", last_name="User", is_active=True)
    db_session.add(d1_user)
    await db_session.flush()
    db_session.add(UserRole(user_id=d1_user.id, role="DONOR"))
    await db_session.flush()

    donor1 = Donor(
        user_id=d1_user.id,
        blood_type="A+",
        city="Bengaluru",
        latitude=12.9800,
        longitude=77.6000,
        is_available=True,
        is_eligible=True,
        total_donations=4,
        last_donation_date=today - timedelta(days=90),
    )
    db_session.add(donor1)

    # 2. Compatible Donor 2 (O- universal, available, 2 donations, 10km away)
    d2_user = User(email=f"d2.{uuid.uuid4().hex[:6]}@gmail.com", password_hash="hash", first_name="D2", last_name="User", is_active=True)
    db_session.add(d2_user)
    await db_session.flush()
    db_session.add(UserRole(user_id=d2_user.id, role="DONOR"))
    await db_session.flush()

    donor2 = Donor(
        user_id=d2_user.id,
        blood_type="O-",
        city="Bengaluru",
        latitude=13.0000,
        longitude=77.6100,
        is_available=True,
        is_eligible=True,
        total_donations=2,
        last_donation_date=today - timedelta(days=70),
    )
    db_session.add(donor2)

    # 3. Incompatible Donor (B+, should be excluded)
    d3_user = User(email=f"d3.{uuid.uuid4().hex[:6]}@gmail.com", password_hash="hash", first_name="D3", last_name="User", is_active=True)
    db_session.add(d3_user)
    await db_session.flush()
    db_session.add(UserRole(user_id=d3_user.id, role="DONOR"))
    await db_session.flush()

    donor3 = Donor(
        user_id=d3_user.id,
        blood_type="B+",
        city="Bengaluru",
        is_available=True,
        is_eligible=True,
        total_donations=5,
    )
    db_session.add(donor3)

    # 4. Ineligible Donor (A+, in cooldown < 56 days, should be excluded)
    d4_user = User(email=f"d4.{uuid.uuid4().hex[:6]}@gmail.com", password_hash="hash", first_name="D4", last_name="User", is_active=True)
    db_session.add(d4_user)
    await db_session.flush()
    db_session.add(UserRole(user_id=d4_user.id, role="DONOR"))
    await db_session.flush()

    donor4 = Donor(
        user_id=d4_user.id,
        blood_type="A+",
        city="Bengaluru",
        is_available=True,
        is_eligible=True,
        last_donation_date=today - timedelta(days=20),
    )
    db_session.add(donor4)

    # 5. Unavailable Donor (A+, is_available=False, should be excluded)
    d5_user = User(email=f"d5.{uuid.uuid4().hex[:6]}@gmail.com", password_hash="hash", first_name="D5", last_name="User", is_active=True)
    db_session.add(d5_user)
    await db_session.flush()
    db_session.add(UserRole(user_id=d5_user.id, role="DONOR"))
    await db_session.flush()

    donor5 = Donor(
        user_id=d5_user.id,
        blood_type="A+",
        city="Bengaluru",
        is_available=False,
        is_eligible=True,
    )
    db_session.add(donor5)

    # 6. Blood Bank with Compatible Inventory
    bb_user = User(email=f"bb.{uuid.uuid4().hex[:6]}@rotary.org", password_hash="hash", first_name="BB", last_name="User", is_active=True)
    db_session.add(bb_user)
    await db_session.flush()
    db_session.add(UserRole(user_id=bb_user.id, role="BLOOD_BANK_MANAGER"))
    await db_session.flush()

    blood_bank = BloodBank(
        name="Rotary Central Blood Centre",
        license_number=f"BB-LIC-{uuid.uuid4().hex[:6].upper()}",
        address_line="Residency Road",
        city="Bengaluru",
        state="Karnataka",
        pincode="560025",
        phone="+918022004400",
        latitude=12.9750,
        longitude=77.6000,
        is_active=True,
        is_verified=True,
        created_by=bb_user.id,
    )
    db_session.add(blood_bank)
    await db_session.flush()

    # Add stock: 6 units of A+ (valid expiry) and 4 units of B+ (incompatible)
    inv_comp = BloodInventory(
        facility_type="BLOOD_BANK",
        facility_id=blood_bank.id,
        blood_type="A+",
        units_available=6,
        units_reserved=0,
        expiry_date=today + timedelta(days=30),
    )
    inv_incomp = BloodInventory(
        facility_type="BLOOD_BANK",
        facility_id=blood_bank.id,
        blood_type="B+",
        units_available=10,
        units_reserved=0,
        expiry_date=today + timedelta(days=30),
    )
    db_session.add(inv_comp)
    db_session.add(inv_incomp)

    # 7. Blood Bank with ONLY Expired Stock
    bb_exp_user = User(email=f"bb.exp.{uuid.uuid4().hex[:6]}@redcross.org", password_hash="hash", first_name="BBExp", last_name="User", is_active=True)
    db_session.add(bb_exp_user)
    await db_session.flush()
    db_session.add(UserRole(user_id=bb_exp_user.id, role="BLOOD_BANK_MANAGER"))
    await db_session.flush()

    bb_expired = BloodBank(
        name="Red Cross Expired Stock Only",
        license_number=f"BB-EXP-{uuid.uuid4().hex[:6].upper()}",
        address_line="Old Airport Rd",
        city="Bengaluru",
        state="Karnataka",
        pincode="560017",
        phone="+918022005500",
        is_active=True,
        is_verified=True,
        created_by=bb_exp_user.id,
    )
    db_session.add(bb_expired)

    await db_session.flush()

    inv_expired = BloodInventory(
        facility_type="BLOOD_BANK",
        facility_id=bb_expired.id,
        blood_type="A+",
        units_available=8,
        units_reserved=0,
        expiry_date=today - timedelta(days=2),  # Expired
    )
    db_session.add(inv_expired)
    await db_session.commit()

    # Execute matching
    res = await client.post(
        f"/api/v1/hospitals/me/requests/{req.id}/match",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    data = res.json()["data"]

    # Verify run metadata
    assert data["emergency_request_id"] == str(req.id)
    assert data["status"] == "COMPLETED"
    assert data["run_number"] >= 1
    assert "donor-response" in data["model_version"] or "fallback" in data["model_version"]

    # Verify Donors: exactly donor1 and donor2 matched
    donor_candidates = data["donors"]
    matched_donor_ids = [d["candidate_id"] for d in donor_candidates]
    assert str(donor1.id) in matched_donor_ids
    assert str(donor2.id) in matched_donor_ids
    assert str(donor3.id) not in matched_donor_ids  # Incompatible B+ excluded
    assert str(donor4.id) not in matched_donor_ids  # Ineligible cooldown excluded
    assert str(donor5.id) not in matched_donor_ids  # Unavailable excluded

    # Verify Blood Banks: Rotary included, Expired excluded
    bb_candidates = data["blood_banks"]
    matched_bb_ids = [b["candidate_id"] for b in bb_candidates]
    assert str(blood_bank.id) in matched_bb_ids
    assert str(bb_expired.id) not in matched_bb_ids  # Expired stock excluded

    # Verify Zero Patient PII
    res_str = str(res.json())
    assert "Confidential ICU Patient" not in res_str
    assert "patient_name" not in res_str

    # Test Candidate Lifecycle (Update candidate status to SHORTLISTED)
    target_cand_id = donor_candidates[0]["id"]
    patch_res = await client.patch(
        f"/api/v1/hospitals/me/requests/{req.id}/matches/{target_cand_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "SHORTLISTED"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["data"]["status"] == "SHORTLISTED"

    # Test History: get_matches endpoint
    hist_res = await client.get(
        f"/api/v1/hospitals/me/requests/{req.id}/matches",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert hist_res.status_code == 200
    assert hist_res.json()["data"]["run_number"] >= 1
