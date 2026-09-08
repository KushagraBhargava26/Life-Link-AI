# backend/scripts/seed_demo_data.py
# LifeLink AI — Demo Seed Data Generator
# Generates linked, reproducible demo personas for evaluation and live walkthroughs.

from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
import datetime
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.database import get_session_factory
from app.modules.auth.models import User, UserRole
from app.modules.blood_bank.models import BloodBank
from app.modules.donor.models import Donor
from app.modules.emergency.models import EmergencyRequest, EmergencyStatusEnum
from app.modules.hospital.models import Hospital, HospitalStaff, HospitalTypeEnum
from app.modules.inventory.models import BloodInventory, InventoryChangeEnum, InventoryHistory


async def seed_data():
    session_factory = get_session_factory()
    async with session_factory() as session:
        print("=" * 60)
        print("LIFELINK AI — SEEDING DEMO ACCOUNTS AND DATA")
        print("=" * 60)

        # 1. ADMIN USER
        admin_email = "admin@lifelink.ai"
        stmt = select(User).where(User.email == admin_email)
        admin_user = (await session.execute(stmt)).scalar_one_or_none()

        if not admin_user:
            admin_user = User(
                id=uuid.uuid4(),
                email=admin_email,
                password_hash=hash_password("Admin@12345"),
                first_name="LifeLink",
                last_name="SuperAdmin",
                phone="+919800000001",
                is_active=True,
                is_verified=True,
            )
            session.add(admin_user)
            await session.flush()

            role1 = UserRole(id=uuid.uuid4(), user_id=admin_user.id, role="SUPER_ADMIN")
            role2 = UserRole(id=uuid.uuid4(), user_id=admin_user.id, role="ADMIN")
            session.add_all([role1, role2])
            print(f"[+] Admin created: {admin_email} (Pass: Admin@12345)")
        else:
            print(f"[*] Admin exists: {admin_email}")

        # 2. HOSPITAL USER & FACILITY
        hosp_email = "hospital.admin@apollo.org"
        stmt = select(User).where(User.email == hosp_email)
        hosp_user = (await session.execute(stmt)).scalar_one_or_none()

        if not hosp_user:
            hosp_user = User(
                id=uuid.uuid4(),
                email=hosp_email,
                password_hash=hash_password("Hospital@12345"),
                first_name="Dr. Rajesh",
                last_name="Verma",
                phone="+919800000002",
                is_active=True,
                is_verified=True,
            )
            session.add(hosp_user)
            await session.flush()

            h_role = UserRole(id=uuid.uuid4(), user_id=hosp_user.id, role="HOSPITAL_ADMIN")
            session.add(h_role)
            print(f"[+] Hospital Admin created: {hosp_email} (Pass: Hospital@12345)")
        else:
            print(f"[*] Hospital Admin exists: {hosp_email}")

        # Hospital Profile
        stmt = select(Hospital).where(Hospital.created_by == hosp_user.id)
        hospital = (await session.execute(stmt)).scalar_one_or_none()

        if not hospital:
            hospital = Hospital(
                id=uuid.uuid4(),
                name="Apollo Apex Care Hospital",
                registration_number="MH-MUM-2024-8841",
                type=HospitalTypeEnum.PRIVATE,
                address_line="Sector 12, Bandra West",
                city="Mumbai",
                state="Maharashtra",
                pincode="400050",
                latitude=19.0760,
                longitude=72.8777,
                phone="+912260001111",
                email="emergency@apollo-apex.org",
                website="https://apollo-apex.example.org",
                bed_count=450,
                has_blood_bank=True,
                license_issue_date=datetime.date(2024, 1, 15),
                license_expiry_date=datetime.date(2029, 1, 14),
                certificate_url="/uploads/certificates/apollo_apex_license.pdf",
                status="ACTIVE",
                is_verified=True,
                is_active=True,
                created_by=hosp_user.id,
            )
            session.add(hospital)
            await session.flush()

            staff = HospitalStaff(
                id=uuid.uuid4(),
                hospital_id=hospital.id,
                user_id=hosp_user.id,
                designation="Chief Medical Officer & Administrator",
                is_primary=True,
                can_manage_inventory=True,
                can_create_requests=True,
            )
            session.add(staff)
            print(f"[+] Hospital facility created: {hospital.name} (ACTIVE, Verified)")
        else:
            print(f"[*] Hospital facility exists: {hospital.name}")

        # 3. BLOOD BANK USER, FACILITY & 8-GROUP INVENTORY
        bb_email = "bloodbank.manager@redcross.org"
        stmt = select(User).where(User.email == bb_email)
        bb_user = (await session.execute(stmt)).scalar_one_or_none()

        if not bb_user:
            bb_user = User(
                id=uuid.uuid4(),
                email=bb_email,
                password_hash=hash_password("BloodBank@12345"),
                first_name="Ananya",
                last_name="Deshmukh",
                phone="+919800000003",
                is_active=True,
                is_verified=True,
            )
            session.add(bb_user)
            await session.flush()

            bb_role = UserRole(id=uuid.uuid4(), user_id=bb_user.id, role="BLOOD_BANK_MANAGER")
            session.add(bb_role)
            print(f"[+] Blood Bank Manager created: {bb_email} (Pass: BloodBank@12345)")
        else:
            print(f"[*] Blood Bank Manager exists: {bb_email}")

        # Blood Bank Facility
        stmt = select(BloodBank).where(BloodBank.created_by == bb_user.id)
        blood_bank = (await session.execute(stmt)).scalar_one_or_none()

        if not blood_bank:
            blood_bank = BloodBank(
                id=uuid.uuid4(),
                name="Central Red Cross Blood Center",
                license_number="BB-MH-2024-0091",
                address_line="Plot 45, Kurla Complex",
                city="Mumbai",
                state="Maharashtra",
                pincode="400070",
                latitude=19.0800,
                longitude=72.8800,
                phone="+912260002222",
                email="coordination@redcross-mumbai.org",
                operating_hours="24/7 Emergency Transfusion Unit",
                is_24_hours=True,
                accepts_walk_in=True,
                license_issue_date=datetime.date(2024, 3, 1),
                license_expiry_date=datetime.date(2029, 2, 28),
                certificate_url="/uploads/certificates/redcross_bb_license.pdf",
                status="ACTIVE",
                is_verified=True,
                is_active=True,
                manager_user_id=bb_user.id,
                created_by=bb_user.id,
            )
            session.add(blood_bank)
            await session.flush()
            print(f"[+] Blood Bank facility created: {blood_bank.name} (ACTIVE, Verified)")
        else:
            print(f"[*] Blood Bank facility exists: {blood_bank.name}")

        # Seed 8 Blood Inventory Stock Groups
        stock_spec = {
            "O-": 12,
            "O+": 25,
            "A-": 8,
            "A+": 30,
            "B-": 6,
            "B+": 20,
            "AB-": 4,
            "AB+": 15,
        }
        now = datetime.datetime.now(datetime.timezone.utc)
        expiry = datetime.date.today() + datetime.timedelta(days=35)

        for b_type, units in stock_spec.items():
            stmt = select(BloodInventory).where(
                BloodInventory.facility_type == "BLOOD_BANK",
                BloodInventory.facility_id == blood_bank.id,
                BloodInventory.blood_type == b_type,
            )
            inv = (await session.execute(stmt)).scalar_one_or_none()
            if not inv:
                inv = BloodInventory(
                    id=uuid.uuid4(),
                    facility_type="BLOOD_BANK",
                    facility_id=blood_bank.id,
                    blood_type=b_type,
                    component="WHOLE_BLOOD",
                    units_available=units,
                    units_reserved=0,
                    minimum_threshold=5,
                    expiry_date=expiry,
                    last_restocked_at=now,
                    created_at=now,
                    updated_at=now,
                )
                session.add(inv)
                await session.flush()

                history = InventoryHistory(
                    id=uuid.uuid4(),
                    inventory_id=inv.id,
                    changed_by=bb_user.id,
                    change_type=InventoryChangeEnum.RESTOCK.value,
                    units_before=0,
                    units_after=units,
                    units_delta=units,
                    reason="Initial demo stock load",
                    created_at=now,
                )
                session.add(history)
        print(f"[+] Seeded 8 blood groups in inventory for {blood_bank.name}")

        # 4. DONOR USER & PROFILE (Compatible O-)
        donor_email = "donor.rahul@example.com"
        stmt = select(User).where(User.email == donor_email)
        donor_user = (await session.execute(stmt)).scalar_one_or_none()

        if not donor_user:
            donor_user = User(
                id=uuid.uuid4(),
                email=donor_email,
                password_hash=hash_password("Donor@12345"),
                first_name="Rahul",
                last_name="Sharma",
                phone="+919800000004",
                is_active=True,
                is_verified=True,
            )
            session.add(donor_user)
            await session.flush()

            d_role = UserRole(id=uuid.uuid4(), user_id=donor_user.id, role="DONOR")
            session.add(d_role)
            print(f"[+] Donor User created: {donor_email} (Pass: Donor@12345)")
        else:
            print(f"[*] Donor User exists: {donor_email}")

        # Donor Profile
        stmt = select(Donor).where(Donor.user_id == donor_user.id)
        donor_profile = (await session.execute(stmt)).scalar_one_or_none()

        if not donor_profile:
            donor_profile = Donor(
                id=uuid.uuid4(),
                user_id=donor_user.id,
                blood_type="O-",
                date_of_birth=datetime.date(1995, 6, 15),
                gender="Male",
                weight_kg=72.0,
                address_line="Flat 402, Sea View Apartments, Dadar",
                city="Mumbai",
                state="Maharashtra",
                pincode="400028",
                latitude=19.0780,
                longitude=72.8750,
                is_available=True,
                is_eligible=True,
                last_donation_date=datetime.date(2026, 6, 10),
                total_donations=4,
            )
            session.add(donor_profile)
            await session.flush()
            print(f"[+] Donor profile created: Rahul Sharma (O-, Eligible, Available)")
        else:
            print(f"[*] Donor profile exists: {donor_user.first_name} {donor_user.last_name}")

        # 5. ACTIVE EMERGENCY REQUISITION
        stmt = select(EmergencyRequest).where(EmergencyRequest.request_number == "EMR-2026-0001")
        emr_req = (await session.execute(stmt)).scalar_one_or_none()

        if not emr_req:
            emr_req = EmergencyRequest(
                id=uuid.uuid4(),
                request_number="EMR-2026-0001",
                requested_by=hosp_user.id,
                patient_name="Priya Nair",
                patient_age=34,
                blood_type="O-",
                units_required=3,
                units_fulfilled=0,
                urgency_level="CRITICAL",
                hospital_name=hospital.name,
                hospital_id=hospital.id,
                facility_address=f"{hospital.name}, {hospital.address_line}, {hospital.city}",
                city="Mumbai",
                latitude=19.0760,
                longitude=72.8777,
                status=EmergencyStatusEnum.MATCHING.value,
                ai_assisted=True,
                notes="Trauma surgery requisition. Urgent O- whole blood units required.",
            )
            session.add(emr_req)
            await session.flush()
            print(f"[+] Emergency request created: {emr_req.request_number} (3 units O- CRITICAL)")
        else:
            print(f"[*] Emergency request exists: {emr_req.request_number}")

        await session.commit()
        print("=" * 60)
        print("SEEDING COMPLETE! ALL DEMO ACCOUNTS READY:")
        print("  - Admin:       admin@lifelink.ai / Admin@12345")
        print("  - Hospital:    hospital.admin@apollo.org / Hospital@12345")
        print("  - Blood Bank:  bloodbank.manager@redcross.org / BloodBank@12345")
        print("  - Donor:       donor.rahul@example.com / Donor@12345")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(seed_data())
