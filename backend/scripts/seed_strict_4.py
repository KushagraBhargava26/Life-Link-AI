# backend/scripts/seed_strict_4.py
# LifeLink AI — Strict 4-Account Seed & Active Sync Pipeline
# Provisions STRICTLY 4 accounts:
#   1. Donor: Priya Verma (A+, Mumbai)
#   2. Hospital: Apollo Hospital Admin (Apollo Hospital Mumbai)
#   3. Blood Bank: Red Cross Blood Bank Manager (Central Red Cross Blood Center)
#   4. System: Super Admin (Lifelink AI Admin)
#
# Also provisions active emergency blood requests linked to Apollo Hospital
# with automated match run calculations for immediate end-to-end synchronization.

from __future__ import annotations

import asyncio
import datetime
import os
import sys
import uuid

# Add backend directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.database import get_db, get_session_factory
from app.modules.auth.models import User, UserRole
from app.modules.blood_bank.models import BloodBank
from app.modules.donor.models import Donor, DonorEmergencyResponse
from app.modules.emergency.models import EmergencyRequest, EmergencyStatusEnum, UrgencyLevelEnum
from app.modules.hospital.models import Hospital, HospitalStaff, HospitalTypeEnum
from app.modules.inventory.models import BloodBankEmergencyResponse, BloodInventory, InventoryHistory
from app.modules.matching.models import (
    MatchCandidate,
    MatchCandidateStatusEnum,
    MatchCandidateTypeEnum,
    MatchRun,
    MatchRunStatusEnum,
)

STRICT_4_EMAILS = {
    "admin@lifelink.ai",
    "hospital.admin@apollo.org",
    "bloodbank.manager@redcross.org",
    "priya.verma@gmail.com",
}


async def purge_all_non_strict_data(db: AsyncSession):
    """Purges any legacy/extra accounts and stale requests to enforce strictly 4 accounts."""
    print("[*] Purging all non-conforming data...")

    # 1. Delete all match candidates and runs
    await db.execute(delete(MatchCandidate))
    await db.execute(delete(MatchRun))

    # 2. Delete all emergency responses
    await db.execute(delete(DonorEmergencyResponse))
    await db.execute(delete(BloodBankEmergencyResponse))

    # 3. Delete emergency requests
    await db.execute(delete(EmergencyRequest))

    # 4. Delete inventory history & inventory
    await db.execute(delete(InventoryHistory))
    await db.execute(delete(BloodInventory))

    # 5. Delete donors, hospital staff, hospitals, blood banks
    await db.execute(delete(Donor))
    await db.execute(delete(HospitalStaff))
    await db.execute(delete(Hospital))
    await db.execute(delete(BloodBank))

    # 6. Delete user roles and users not in STRICT_4_EMAILS
    await db.execute(delete(UserRole))
    await db.execute(delete(User))

    await db.commit()
    print("[+] Database cleanly purged for strict 4-account provisioning.")


async def seed_strict_accounts():
    session_factory = get_session_factory()
    async with session_factory() as db:
        print("=" * 70)
        print("LIFELINK AI — STRICT 4-ACCOUNT INITIALIZATION & SYNC SEED")
        print("=" * 70)

        # Purge everything to guarantee strict 4 accounts
        await purge_all_non_strict_data(db)

        now = datetime.datetime.now(datetime.timezone.utc)
        today = datetime.date.today()

        # =====================================================================
        # 1. DEMO/SYSTEM ACCOUNT: Super Admin
        # =====================================================================
        admin_user = User(
            id=uuid.uuid4(),
            email="admin@lifelink.ai",
            password_hash=get_password_hash("Admin@12345"),
            first_name="System",
            last_name="Administrator",
            phone="+91-9800000000",
            is_active=True,
            is_verified=True,
        )
        db.add(admin_user)
        await db.flush()

        admin_role = UserRole(
            id=uuid.uuid4(),
            user_id=admin_user.id,
            role="SUPER_ADMIN",
        )
        db.add(admin_role)
        print(f"[+] 1/4 Provisioned System Admin: {admin_user.email}")

        # =====================================================================
        # 2. HOSPITAL ACCOUNT: Apollo Hospital Admin
        # =====================================================================
        hosp_admin_user = User(
            id=uuid.uuid4(),
            email="hospital.admin@apollo.org",
            password_hash=get_password_hash("Hospital@12345"),
            first_name="Rajesh",
            last_name="Mehta",
            phone="+91-9820123456",
            is_active=True,
            is_verified=True,
        )
        db.add(hosp_admin_user)
        await db.flush()

        hosp_role = UserRole(
            id=uuid.uuid4(),
            user_id=hosp_admin_user.id,
            role="HOSPITAL_ADMIN",
        )
        db.add(hosp_role)

        apollo_hospital = Hospital(
            id=uuid.uuid4(),
            name="Apollo Hospital Mumbai",
            registration_number="MH-MUM-HOSP-2024-0042",
            type=HospitalTypeEnum.PRIVATE,
            address_line="Parsik Hill Road, Sector 23, CBD Belapur",
            city="Mumbai",
            state="Maharashtra",
            pincode="400614",
            latitude=19.01780000,
            longitude=72.84780000,
            phone="+91-22-2775-5000",
            email="trauma@apollo.org",
            website="https://apollohospitals.com/mumbai",
            bed_count=500,
            has_blood_bank=True,
            is_active=True,
            is_verified=True,
            created_by=hosp_admin_user.id,
        )
        db.add(apollo_hospital)
        await db.flush()

        hosp_staff = HospitalStaff(
            id=uuid.uuid4(),
            hospital_id=apollo_hospital.id,
            user_id=hosp_admin_user.id,
            designation="Chief Medical Administrator",
            is_primary=True,
            can_create_requests=True,
            can_manage_inventory=True,
        )
        db.add(hosp_staff)
        print(f"[+] 2/4 Provisioned Hospital Account: {hosp_admin_user.email} -> {apollo_hospital.name}")

        # =====================================================================
        # 3. BLOOD BANK ACCOUNT: Red Cross Blood Bank Manager
        # =====================================================================
        bb_user = User(
            id=uuid.uuid4(),
            email="bloodbank.manager@redcross.org",
            password_hash=get_password_hash("BloodBank@12345"),
            first_name="Sunita",
            last_name="Deshmukh",
            phone="+91-9819876543",
            is_active=True,
            is_verified=True,
        )
        db.add(bb_user)
        await db.flush()

        bb_role = UserRole(
            id=uuid.uuid4(),
            user_id=bb_user.id,
            role="BLOOD_BANK_MANAGER",
        )
        db.add(bb_role)

        red_cross_bb = BloodBank(
            id=uuid.uuid4(),
            name="Central Red Cross Blood Center",
            license_number="MH-BB-2023-0091",
            address_line="141 Shaheed Bhagat Singh Road, Fort",
            city="Mumbai",
            state="Maharashtra",
            pincode="400001",
            latitude=19.01850000,
            longitude=72.84300000,
            phone="+91-22-2266-1234",
            email="dispatch@redcrossblood.org",
            operating_hours="24/7 Emergency Dispatch",
            is_24_hours=True,
            accepts_walk_in=True,
            is_active=True,
            is_verified=True,
            manager_user_id=bb_user.id,
            created_by=bb_user.id,
        )
        db.add(red_cross_bb)
        await db.flush()

        # Seed full inventory (8 groups)
        inventory_items = [
            ("A+", 18, 4),
            ("A-", 6, 1),
            ("B+", 22, 5),
            ("B-", 5, 0),
            ("AB+", 10, 2),
            ("AB-", 4, 0),
            ("O+", 25, 6),
            ("O-", 8, 2),
        ]
        for b_type, avail, reserved in inventory_items:
            inv = BloodInventory(
                id=uuid.uuid4(),
                facility_type="BLOOD_BANK",
                facility_id=red_cross_bb.id,
                blood_type=b_type,
                component="WHOLE_BLOOD",
                units_available=avail,
                units_reserved=reserved,
                minimum_threshold=5,
                last_restocked_at=now - datetime.timedelta(days=1),
                expiry_date=today + datetime.timedelta(days=35),
            )
            db.add(inv)
        print(f"[+] 3/4 Provisioned Blood Bank Account: {bb_user.email} -> {red_cross_bb.name} (8 Blood Groups Seeded)")

        # =====================================================================
        # 4. DONOR ACCOUNT: Priya Verma (A+, Mumbai)
        # =====================================================================
        donor_user = User(
            id=uuid.uuid4(),
            email="priya.verma@gmail.com",
            password_hash=get_password_hash("Priya@12345"),
            first_name="Priya",
            last_name="Verma",
            phone="+91-9876543210",
            is_active=True,
            is_verified=True,
        )
        db.add(donor_user)
        await db.flush()

        donor_role = UserRole(
            id=uuid.uuid4(),
            user_id=donor_user.id,
            role="DONOR",
        )
        db.add(donor_role)

        priya_donor = Donor(
            id=uuid.uuid4(),
            user_id=donor_user.id,
            blood_type="A+",
            city="Mumbai",
            state="Maharashtra",
            pincode="400050",
            address_line="Bandra West, Hill Road",
            date_of_birth=datetime.date(1996, 4, 12),
            weight_kg=54.0,
            gender="FEMALE",
            is_available=True,
            is_eligible=True,
            last_donation_date=today - datetime.timedelta(days=200),  # 200 days ago > 112-day cooldown -> fully eligible!
            total_donations=4,
            latitude=19.07600000,
            longitude=72.87770000,
        )
        db.add(priya_donor)
        await db.flush()
        print(f"[+] 4/4 Provisioned Donor Account: {donor_user.email} -> Priya Verma (A+, Mumbai, Eligible)")

        # =====================================================================
        # ACTIVE EMERGENCY BLOOD REQUESTS (Created by Hospital Account)
        # =====================================================================
        # Requisition 1: A+ Critical Emergency (Directly matches Priya Verma!)
        req1 = EmergencyRequest(
            id=uuid.uuid4(),
            request_number="EMR-2026-0001",
            requested_by=hosp_admin_user.id,
            hospital_id=apollo_hospital.id,
            patient_name="Aarav Sharma",
            patient_age=34,
            blood_type="A+",
            units_required=2,
            units_fulfilled=0,
            urgency_level=UrgencyLevelEnum.CRITICAL.value,
            hospital_name=apollo_hospital.name,
            facility_address=f"{apollo_hospital.name}, {apollo_hospital.address_line}, {apollo_hospital.city}",
            city="Mumbai",
            latitude=apollo_hospital.latitude,
            longitude=apollo_hospital.longitude,
            status=EmergencyStatusEnum.MATCHING.value,
            ai_assisted=True,
            notes="Trauma ICU - Acute hemorrhagic shock following road accident. Requires urgent whole blood transfusion.",
        )
        db.add(req1)

        # Requisition 2: O- High Urgency Emergency (Compatible with O- / Universal)
        req2 = EmergencyRequest(
            id=uuid.uuid4(),
            request_number="EMR-2026-0002",
            requested_by=hosp_admin_user.id,
            hospital_id=apollo_hospital.id,
            patient_name="Meera Iyer",
            patient_age=28,
            blood_type="O-",
            units_required=1,
            units_fulfilled=0,
            urgency_level=UrgencyLevelEnum.HIGH.value,
            hospital_name=apollo_hospital.name,
            facility_address=f"{apollo_hospital.name}, {apollo_hospital.address_line}, {apollo_hospital.city}",
            city="Mumbai",
            latitude=apollo_hospital.latitude,
            longitude=apollo_hospital.longitude,
            status=EmergencyStatusEnum.MATCHING.value,
            ai_assisted=True,
            notes="Emergency Obstetric Care - Post-partum hemorrhage. Universal donor units needed.",
        )
        db.add(req2)
        await db.flush()

        # =====================================================================
        # ACTIVE MATCH RUN & CANDIDATES FOR REQUISITION 1 (EMR-2026-0001)
        # =====================================================================
        # Haversine distance between Apollo Mumbai (19.0178, 72.8478) and Priya Verma (19.0760, 72.8777) is ~7.2 km
        # Haversine distance between Apollo Mumbai and Red Cross Blood Bank (19.0185, 72.8430) is ~0.5 km
        match_run_1 = MatchRun(
            id=uuid.uuid4(),
            emergency_request_id=req1.id,
            run_number=1,
            status=MatchRunStatusEnum.COMPLETED,
            model_version="donor-response-v1",
            algorithm="hybrid_ai_ranking",
            search_radius_km=50.0,
            candidates_evaluated=2,
            donors_matched=1,
            blood_banks_matched=1,
            execution_duration_ms=42.5,
            executed_by=hosp_admin_user.id,
        )
        db.add(match_run_1)
        await db.flush()

        # Blood Bank Candidate
        cand_bb = MatchCandidate(
            id=uuid.uuid4(),
            match_run_id=match_run_1.id,
            emergency_request_id=req1.id,
            candidate_type=MatchCandidateTypeEnum.BLOOD_BANK,
            blood_bank_id=red_cross_bb.id,
            rank=1,
            total_score=0.9850,
            compatibility_score=1.0,
            proximity_score=0.9900,
            availability_score=1.0,
            ai_score=None,
            distance_km=0.52,
            units_available=18,
            status=MatchCandidateStatusEnum.PROPOSED,
            explanation=[
                "Verified cold storage: 18 compatible A+ units on hand",
                "Exact ABO/Rh match available",
                "24/7 operating facility",
                "Located 0.5 km from trauma facility",
            ],
        )
        db.add(cand_bb)

        # Donor Candidate: Priya Verma
        cand_donor = MatchCandidate(
            id=uuid.uuid4(),
            match_run_id=match_run_1.id,
            emergency_request_id=req1.id,
            candidate_type=MatchCandidateTypeEnum.DONOR,
            donor_id=priya_donor.id,
            rank=2,
            total_score=0.9420,
            compatibility_score=1.0,
            proximity_score=0.8560,
            availability_score=1.0,
            ai_score=0.92,
            distance_km=7.24,
            units_available=1,
            status=MatchCandidateStatusEnum.PROPOSED,
            explanation=[
                "Exact compatible blood type (A+)",
                "Active & ready voluntary donor",
                "Medically eligible (200 days since last donation)",
                "Located 7.2 km away in Bandra West, Mumbai",
            ],
        )
        db.add(cand_donor)

        await db.commit()

        print("\n" + "=" * 70)
        print("STRICT 4-ACCOUNT SEED COMPLETE & SYNCHRONIZED!")
        print("=" * 70)
        print("1. DONOR ACCOUNT:")
        print("   Email:    priya.verma@gmail.com")
        print("   Password: Priya@12345")
        print("   Profile:  Priya Verma | A+ | Mumbai | Female (112-day cooldown eligible)")
        print("   Sync:     Instantly sees EMR-2026-0001 in Compatible Opportunities!")
        print("\n2. HOSPITAL ACCOUNT:")
        print("   Email:    hospital.admin@apollo.org")
        print("   Password: Hospital@12345")
        print("   Facility: Apollo Hospital Mumbai | Trauma Center")
        print("   Sync:     Has 2 Active Requisitions (EMR-2026-0001, EMR-2026-0002)")
        print("             Match Workspace shows Red Cross (0.5km) & Priya Verma (7.2km)!")
        print("\n3. BLOOD BANK ACCOUNT:")
        print("   Email:    bloodbank.manager@redcross.org")
        print("   Password: BloodBank@12345")
        print("   Facility: Central Red Cross Blood Center Mumbai (8 Groups In Stock)")
        print("\n4. DEMO/SYSTEM ACCOUNT:")
        print("   Email:    admin@lifelink.ai")
        print("   Password: Admin@12345")
        print("   Role:     Super Administrator")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(seed_strict_accounts())
