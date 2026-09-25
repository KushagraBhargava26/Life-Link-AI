# backend/scripts/reset_to_demo.py
# LifeLink AI — Database Reset to Demo State
# Removes all manually created accounts, blood requests, and donor responses.
# Keeps ONLY the 4 official demo personas and their linked data.
# Safe to run at any time — re-seeds missing demo data automatically.

from __future__ import annotations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
import uuid
import datetime

from sqlalchemy import delete, select, not_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session_factory

# ---------------------------------------------------------------------------
# Official demo account emails — these are NEVER deleted
# ---------------------------------------------------------------------------
DEMO_EMAILS = {
    "admin@lifelink.ai",
    "hospital.admin@apollo.org",
    "bloodbank.manager@redcross.org",
    "donor.rahul@example.com",
}


async def reset():
    session_factory = get_session_factory()
    async with session_factory() as session:
        print("=" * 60)
        print("LIFELINK AI — RESETTING DATABASE TO DEMO STATE")
        print("=" * 60)

        # ----------------------------------------------------------------
        # Import all models needed
        # ----------------------------------------------------------------
        from app.modules.auth.models import User, UserRole
        from app.modules.donor.models import Donor, DonorEmergencyResponse
        from app.modules.hospital.models import Hospital, HospitalStaff
        from app.modules.blood_bank.models import BloodBank
        from app.modules.emergency.models import EmergencyRequest
        from app.modules.matching.models import MatchRun, MatchCandidate
        from app.modules.inventory.models import BloodInventory, InventoryHistory, BloodBankEmergencyResponse

        # ----------------------------------------------------------------
        # Step 1: Identify demo user IDs (we will never touch these)
        # ----------------------------------------------------------------
        result = await session.execute(
            select(User.id, User.email).where(User.email.in_(DEMO_EMAILS))
        )
        demo_users = {row.email: row.id for row in result}

        print(f"\n[*] Found {len(demo_users)} demo account(s) in DB:")
        for email, uid in demo_users.items():
            print(f"    - {email} ({uid})")

        if len(demo_users) == 0:
            print("\n[!] No demo accounts found — running full seed first...")

        # ----------------------------------------------------------------
        # Step 2: Remove ALL emergency requests not created by the hospital demo account
        # ----------------------------------------------------------------
        hospital_user_id = demo_users.get("hospital.admin@apollo.org")

        # Get all emergency request IDs that are NOT from hospital demo
        non_demo_requests_stmt = select(EmergencyRequest.id).where(
            EmergencyRequest.requested_by != hospital_user_id
            if hospital_user_id
            else EmergencyRequest.id.isnot(None)
        )
        non_demo_req_ids = (await session.execute(non_demo_requests_stmt)).scalars().all()

        if non_demo_req_ids:
            # Delete match candidates first (FK dependency)
            await session.execute(
                delete(MatchCandidate).where(
                    MatchCandidate.emergency_request_id.in_(non_demo_req_ids)
                )
            )
            # Delete match runs
            await session.execute(
                delete(MatchRun).where(
                    MatchRun.emergency_request_id.in_(non_demo_req_ids)
                )
            )
            # Delete donor emergency responses
            await session.execute(
                delete(DonorEmergencyResponse).where(
                    DonorEmergencyResponse.emergency_request_id.in_(non_demo_req_ids)
                )
            )
            # Delete blood bank emergency responses
            await session.execute(
                delete(BloodBankEmergencyResponse).where(
                    BloodBankEmergencyResponse.emergency_request_id.in_(non_demo_req_ids)
                )
            )
            # Now delete the requests themselves
            await session.execute(
                delete(EmergencyRequest).where(
                    EmergencyRequest.id.in_(non_demo_req_ids)
                )
            )
            print(f"\n[+] Removed {len(non_demo_req_ids)} non-demo emergency request(s).")
        else:
            print("\n[*] No non-demo emergency requests found.")

        # ----------------------------------------------------------------
        # Step 3: Clean all donor responses from the demo donor to non-demo requests
        #         (these got cascade-deleted above, but clean any orphans)
        # ----------------------------------------------------------------
        donor_user_id = demo_users.get("donor.rahul@example.com")
        if donor_user_id:
            # Find the demo donor's profile ID
            donor_profile = (await session.execute(
                select(Donor).where(Donor.user_id == donor_user_id)
            )).scalar_one_or_none()

            if donor_profile:
                # Find responses for requests that no longer exist (orphan cleanup)
                all_request_ids_stmt = select(EmergencyRequest.id)
                all_req_ids = set((await session.execute(all_request_ids_stmt)).scalars().all())

                orphan_responses_stmt = select(DonorEmergencyResponse).where(
                    DonorEmergencyResponse.donor_id == donor_profile.id,
                    ~DonorEmergencyResponse.emergency_request_id.in_(all_req_ids) if all_req_ids else True
                )
                orphan_responses = (await session.execute(orphan_responses_stmt)).scalars().all()
                if orphan_responses:
                    for r in orphan_responses:
                        await session.delete(r)
                    print(f"[+] Removed {len(orphan_responses)} orphan donor response(s).")

        # ----------------------------------------------------------------
        # Step 4: Remove all non-demo users and their linked data
        # ----------------------------------------------------------------
        non_demo_users_stmt = select(User).where(
            ~User.email.in_(DEMO_EMAILS)
        )
        non_demo_users = (await session.execute(non_demo_users_stmt)).scalars().all()

        removed_users = 0
        for user in non_demo_users:
            # Remove donor profile + responses
            donor = (await session.execute(
                select(Donor).where(Donor.user_id == user.id)
            )).scalar_one_or_none()

            if donor:
                # Remove donor emergency responses
                await session.execute(
                    delete(DonorEmergencyResponse).where(
                        DonorEmergencyResponse.donor_id == donor.id
                    )
                )
                await session.delete(donor)

            # Remove hospital staff records
            await session.execute(
                delete(HospitalStaff).where(HospitalStaff.user_id == user.id)
            )

            # Remove user roles
            await session.execute(
                delete(UserRole).where(UserRole.user_id == user.id)
            )

            # Remove the user
            await session.delete(user)
            removed_users += 1

        if removed_users:
            print(f"[+] Removed {removed_users} non-demo user account(s) and their data.")
        else:
            print("[*] No non-demo user accounts found.")

        # ----------------------------------------------------------------
        # Step 5: Flush changes, then re-seed to ensure demo data is complete
        # ----------------------------------------------------------------
        await session.commit()
        print("\n[*] Database cleaned. Re-seeding demo accounts...")

    # Re-run the seed script to ensure all demo data is present and correct
    from scripts.seed_demo_data import seed_data
    await seed_data()

    print("\n" + "=" * 60)
    print("RESET COMPLETE — Demo accounts ready:")
    print("  Admin:       admin@lifelink.ai / Admin@12345")
    print("  Hospital:    hospital.admin@apollo.org / Hospital@12345")
    print("  Blood Bank:  bloodbank.manager@redcross.org / BloodBank@12345")
    print("  Donor:       donor.rahul@example.com / Donor@12345")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(reset())
