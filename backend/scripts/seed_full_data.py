import asyncio
import datetime
import uuid
import sys
import os

# Add backend dir to sys.path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.core.security import get_password_hash
from app.modules.auth.models import User, UserRole
from app.modules.donor.models import Donor
from app.modules.hospital.models import Hospital
from app.modules.blood_bank.models import BloodBank
from app.modules.emergency.models import EmergencyRequest, EmergencyStatusEnum


async def get_or_create_user(db: AsyncSession, email: str, role_name: str, first_name: str, last_name: str, password: str, phone: str = None):
    stmt = select(User).where(User.email == email)
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user:
        user = User(
            id=uuid.uuid4(),
            email=email,
            password_hash=get_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            is_active=True,
            is_verified=True,
            phone=phone
        )
        db.add(user)
        await db.flush()
        
        user_role = UserRole(
            id=uuid.uuid4(),
            user_id=user.id,
            role=role_name
        )
        db.add(user_role)
        
        await db.commit()
        await db.refresh(user)
        print(f"Created user: {email}")
    else:
        print(f"User already exists: {email}")
    return user

async def seed_data():
    async for db in get_db():
        print("Starting seeding process...")

        # REAL USERS
        # 1. Priya Verma - DONOR
        u1 = await get_or_create_user(db, "priya.verma@gmail.com", "DONOR", "Priya", "Verma", "Priya@12345", "+91-9876543210")
        donor1 = (await db.execute(select(Donor).where(Donor.user_id == u1.id))).scalar_one_or_none()
        if not donor1:
            d1 = Donor(
                id=uuid.uuid4(),
                user_id=u1.id,
                blood_type="A+",
                city="Mumbai",
                state="Maharashtra",
                date_of_birth=datetime.date(1995, 3, 15),
                weight_kg=52.0,
                gender="FEMALE",
                is_available=True,
                is_eligible=True,
                last_donation_date=datetime.date.today() - datetime.timedelta(days=200),
                latitude=19.0760,
                longitude=72.8777
            )
            db.add(d1)
        
        # 2. Arjun Singh - DONOR
        u2 = await get_or_create_user(db, "arjun.singh@gmail.com", "DONOR", "Arjun", "Singh", "Arjun@12345", "+91-9765432109")
        donor2 = (await db.execute(select(Donor).where(Donor.user_id == u2.id))).scalar_one_or_none()
        if not donor2:
            d2 = Donor(
                id=uuid.uuid4(),
                user_id=u2.id,
                blood_type="B+",
                city="Delhi",
                state="Delhi",
                date_of_birth=datetime.date(1990, 7, 22),
                weight_kg=75.0,
                gender="MALE",
                is_available=True,
                is_eligible=True,
                last_donation_date=datetime.date.today() - datetime.timedelta(days=90),
                latitude=28.7041,
                longitude=77.1025
            )
            db.add(d2)

        # 3. Dr. Sneha Patel - HOSPITAL_ADMIN
        u3 = await get_or_create_user(db, "dr.sneha.patel@gmail.com", "HOSPITAL_ADMIN", "Sneha", "Patel", "Sneha@12345")
        hosp1 = (await db.execute(select(Hospital).where(Hospital.created_by == u3.id))).scalar_one_or_none()
        if not hosp1:
            h1 = Hospital(
                id=uuid.uuid4(),
                created_by=u3.id,
                name="Bangalore City Medical Center",
                registration_number="REG-BLR-001",
                address_line="123 Health Ave",
                city="Bangalore",
                state="Karnataka",
                pincode="560001",
                is_verified=True,
                phone="+91-8012345678", email="contact@blr-medical.com", type="PRIVATE", latitude=12.9716,
                longitude=77.5946
            )
            db.add(h1)
            await db.flush()
            from app.modules.hospital.models import HospitalStaff
            hs1 = HospitalStaff(
                hospital_id=h1.id,
                user_id=u3.id,
                designation="Chief Administrator / Founder",
                is_primary=True,
                can_manage_inventory=True,
                can_create_requests=True,
            )
            db.add(hs1)
            hosp1 = h1

        # 4. Ravi Kumar - BLOOD_BANK_MANAGER
        u4 = await get_or_create_user(db, "ravi.kumar@gmail.com", "BLOOD_BANK_MANAGER", "Ravi", "Kumar", "Ravi@12345")
        bb1 = (await db.execute(select(BloodBank).where(BloodBank.manager_user_id == u4.id))).scalar_one_or_none()
        if not bb1:
            b1 = BloodBank(
                id=uuid.uuid4(),
                manager_user_id=u4.id,
                created_by=u4.id,
                name="Chennai Life Blood Bank",
                license_number="LIC-CHN-002",
                address_line="45 Life Street",
                city="Chennai",
                state="Tamil Nadu",
                pincode="600001",
                phone="+91-4412345678",
                email="contact@chennai-bloodbank.com",
                is_verified=True,
                latitude=13.0827,
                longitude=80.2707
            )
            db.add(b1)

        # DEMO ACCOUNTS
        # 5. Admin
        await get_or_create_user(db, "admin@lifelink.ai", "SYSTEM_ADMIN", "System", "Admin", "Admin@12345")
        
        # 6. Hospital
        u6 = await get_or_create_user(db, "hospital.admin@apollo.org", "HOSPITAL_ADMIN", "Apollo", "Admin", "Hospital@12345")
        hosp2 = (await db.execute(select(Hospital).where(Hospital.created_by == u6.id))).scalar_one_or_none()
        if not hosp2:
            h2 = Hospital(
                id=uuid.uuid4(),
                created_by=u6.id,
                name="Apollo Hospital Mumbai",
                registration_number="REG-MUM-AP1",
                address_line="Marine Drive",
                city="Mumbai",
                state="Maharashtra",
                pincode="400020",
                type="PRIVATE",
                phone="+91-2212345678",
                email="admin@apollo.org",
                is_verified=True,
                latitude=18.9440,
                longitude=72.8238
            )
            db.add(h2)
            await db.flush()
            from app.modules.hospital.models import HospitalStaff
            hs2 = HospitalStaff(
                hospital_id=h2.id,
                user_id=u6.id,
                designation="Admin",
                is_primary=True,
                can_manage_inventory=True,
                can_create_requests=True,
            )
            db.add(hs2)

        # 7. Blood Bank
        u7 = await get_or_create_user(db, "bloodbank.manager@redcross.org", "BLOOD_BANK_MANAGER", "RedCross", "Manager", "BloodBank@12345")
        bb2 = (await db.execute(select(BloodBank).where(BloodBank.manager_user_id == u7.id))).scalar_one_or_none()
        if not bb2:
            b2 = BloodBank(
                id=uuid.uuid4(),
                manager_user_id=u7.id,
                created_by=u7.id,
                name="Central Red Cross Blood Center",
                license_number="LIC-MUM-RC1",
                address_line="Colaba",
                city="Mumbai",
                state="Maharashtra",
                pincode="400005",
                phone="+91-2298765432",
                email="manager@redcross.org",
                is_verified=True,
                latitude=18.9154,
                longitude=72.8259
            )
            db.add(b2)

        # 8. Donor
        u8 = await get_or_create_user(db, "donor.rahul@example.com", "DONOR", "Rahul", "Sharma", "Donor@12345")
        donor8 = (await db.execute(select(Donor).where(Donor.user_id == u8.id))).scalar_one_or_none()
        if not donor8:
            d8 = Donor(
                id=uuid.uuid4(),
                user_id=u8.id,
                blood_type="O-",
                city="Mumbai",
                state="Maharashtra",
                date_of_birth=datetime.date(1992, 5, 10),
                weight_kg=68.0,
                gender="MALE",
                is_available=True,
                is_eligible=True,
                last_donation_date=datetime.date.today() - datetime.timedelta(days=200),
                latitude=19.0760,
                longitude=72.8777
            )
            db.add(d8)

        # Emergency Request 2
        req2 = (await db.execute(select(EmergencyRequest).where(EmergencyRequest.request_number == "EMR-2026-0002"))).scalar_one_or_none()
        if not req2 and hosp1:
            r2 = EmergencyRequest(
                id=uuid.uuid4(),
                hospital_id=hosp1.id,
                request_number="EMR-2026-0002",
                blood_type="B+",
                units_required=2,
                units_fulfilled=0,
                urgency_level="HIGH",
                status=EmergencyStatusEnum.PENDING.value,
                hospital_name=hosp1.name,
                facility_address=hosp1.address_line,
                city=hosp1.city,
                requested_by_id=u3.id
            )
            db.add(r2)
            print("Created EmergencyRequest EMR-2026-0002")

        await db.commit()
        print("Data seed complete.")
        return

if __name__ == "__main__":
    asyncio.run(seed_data())
