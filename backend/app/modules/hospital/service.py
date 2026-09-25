# backend/app/modules/hospital/service.py
# LifeLink AI — Hospital Module Business Logic Service
# Architecture Reference: ARCHITECTURE.md Section 27; API.md Section 8

from __future__ import annotations

import uuid
from typing import Any, Optional

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.emergency.models import EmergencyRequest, EmergencyStatusEnum
from app.modules.emergency.schemas import EmergencyRequestCreateSchema
from app.modules.emergency.service import EmergencyService
from app.modules.hospital.exceptions import (
    HospitalAlreadyExistsError,
    HospitalNotFoundError,
    HospitalPermissionDeniedError,
)
from app.modules.hospital.models import Hospital, HospitalStaff
from app.modules.hospital.repository import HospitalRepository
from app.modules.hospital.schemas import HospitalCreateSchema, HospitalUpdateSchema

logger = structlog.get_logger(__name__)


class HospitalService:
    """Service handling business logic for hospitals and affiliated emergency requests."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = HospitalRepository(db)

    async def create_profile(
        self, data: HospitalCreateSchema, user_id: uuid.UUID
    ) -> Hospital:
        """Create a new hospital profile and link creating user as primary administrator."""
        # 1. Check if user already owns an active hospital
        existing = await self.repository.get_by_user_id(user_id)
        if existing:
            raise HospitalAlreadyExistsError(
                "You already have a hospital facility associated with your account"
            )

        # 2. Check registration number uniqueness if provided
        if data.registration_number:
            conflict = await self.repository.get_by_registration_number(data.registration_number)
            if conflict:
                raise HospitalAlreadyExistsError(
                    f"A hospital with registration number '{data.registration_number}' is already registered"
                )

        hospital = Hospital(
            name=data.name,
            registration_number=data.registration_number,
            type=data.type,
            address_line=data.address_line,
            city=data.city,
            state=data.state,
            pincode=data.pincode,
            latitude=data.latitude,
            longitude=data.longitude,
            phone=data.phone,
            email=data.email,
            website=data.website,
            bed_count=data.bed_count,
            has_blood_bank=data.has_blood_bank,
            license_issue_date=data.license_issue_date,
            license_expiry_date=data.license_expiry_date,
            certificate_url=data.certificate_url,
            status=data.status or "ACTIVE",
            is_verified=bool(data.registration_number or data.license_issue_date or data.certificate_url),
            is_active=True,
            created_by=user_id,
        )
        created = await self.repository.create(hospital)

        # Add creator as primary staff
        staff = HospitalStaff(
            hospital_id=created.id,
            user_id=user_id,
            designation="Chief Administrator / Founder",
            is_primary=True,
            can_manage_inventory=True,
            can_create_requests=True,
        )
        await self.repository.add_staff(staff)
        await self.db.commit()
        await self.db.refresh(created)
        logger.info("hospital_profile_created", hospital_id=str(created.id), user_id=str(user_id))
        return created

    async def get_my_hospital(self, user_id: uuid.UUID) -> Hospital:
        hospital = await self.repository.get_by_user_id(user_id)
        if not hospital:
            raise HospitalNotFoundError("No hospital facility profile associated with your account")
        return hospital

    async def update_my_hospital(
        self, data: HospitalUpdateSchema, user_id: uuid.UUID
    ) -> Hospital:
        hospital = await self.get_my_hospital(user_id)

        update_data = data.model_dump(exclude_unset=True)
        if "registration_number" in update_data and update_data["registration_number"]:
            reg = update_data["registration_number"]
            conflict = await self.repository.get_by_registration_number(reg)
            if conflict and conflict.id != hospital.id:
                raise HospitalAlreadyExistsError(
                    f"Registration number '{reg}' is already used by another hospital"
                )

        for key, value in update_data.items():
            setattr(hospital, key, value)

        updated = await self.repository.update(hospital)
        await self.db.commit()
        await self.db.refresh(updated)
        logger.info("hospital_profile_updated", hospital_id=str(updated.id), user_id=str(user_id))
        return updated

    async def get_hospital_by_id(self, hospital_id: uuid.UUID) -> Hospital:
        hospital = await self.repository.get_by_id(hospital_id)
        if not hospital:
            raise HospitalNotFoundError(f"Hospital with ID '{hospital_id}' not found")
        return hospital

    async def list_hospitals(
        self,
        city: Optional[str] = None,
        is_verified: Optional[bool] = None,
        has_blood_bank: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Hospital], int]:
        return await self.repository.list_hospitals(
            city=city,
            is_verified=is_verified,
            has_blood_bank=has_blood_bank,
            limit=limit,
            offset=offset,
        )

    async def get_hospital_dashboard(self, user_id: uuid.UUID) -> dict[str, Any]:
        """Fetch live operational dashboard state for the hospital."""
        hospital = await self.get_my_hospital(user_id)
        requests, total = await self.repository.list_hospital_requests(hospital.id, limit=10, offset=0)

        active_count = sum(
            1 for r in requests if r.status in (
                EmergencyStatusEnum.PENDING.value,
                EmergencyStatusEnum.MATCHING.value,
                EmergencyStatusEnum.NOTIFIED.value,
                EmergencyStatusEnum.CONFIRMED.value,
                EmergencyStatusEnum.IN_PROGRESS.value,
            )
        )
        pending_count = sum(
            1 for r in requests if r.status == EmergencyStatusEnum.PENDING.value
        )

        recent = [
            {
                "id": str(r.id),
                "request_number": r.request_number,
                "blood_type": r.blood_type,
                "units_required": r.units_required,
                "units_fulfilled": r.units_fulfilled,
                "urgency_level": r.urgency_level,
                "status": r.status,
                "city": r.city,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in requests
        ]

        return {
            "hospital": hospital,
            "active_requests_count": active_count,
            "pending_requests_count": pending_count,
            "recent_requests": recent,
        }

    async def list_hospital_requests(
        self, user_id: uuid.UUID, limit: int = 20, offset: int = 0
    ) -> tuple[list[dict[str, Any]], int]:
        hospital = await self.get_my_hospital(user_id)
        requests, total = await self.repository.list_hospital_requests(hospital.id, limit=limit, offset=offset)
        items = [
            {
                "id": str(r.id),
                "request_number": r.request_number,
                "blood_type": r.blood_type,
                "units_required": r.units_required,
                "units_fulfilled": r.units_fulfilled,
                "urgency_level": r.urgency_level,
                "status": r.status,
                "hospital_name": hospital.name,
                "city": r.city,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in requests
        ]
        return items, total

    async def create_hospital_emergency_request(
        self, data: EmergencyRequestCreateSchema, user_id: uuid.UUID
    ) -> EmergencyRequest:
        """Create a new emergency requisition linked to this hospital."""
        hospital = await self.get_my_hospital(user_id)

        if hospital.status in ("SUSPENDED", "BLOCKED"):
            raise HospitalPermissionDeniedError(
                f"Hospital facility is currently {hospital.status}. Cannot create emergency requisitions."
            )

        # Set hospital details on the request schema
        data.hospital_name = hospital.name
        data.city = hospital.city
        if not data.facility_address:
            data.facility_address = f"{hospital.name}, {hospital.address_line}, {hospital.city}"

        emergency_service = EmergencyService(self.db)
        created = await emergency_service.create_request(data, requested_by=user_id)

        # Link hospital_id
        created.hospital_id = hospital.id
        await self.db.commit()
        await self.db.refresh(created)
        logger.info(
            "hospital_emergency_request_created",
            request_id=str(created.id),
            hospital_id=str(hospital.id),
            user_id=str(user_id),
        )
        return created

    async def delete_account(self, user_id: uuid.UUID) -> None:
        from app.modules.auth.models import User as UserModel
        import datetime
        from sqlalchemy import select
        
        hospital = await self.get_my_hospital(user_id)
        
        # Soft delete hospital
        now = datetime.datetime.now(datetime.timezone.utc)
        hospital.deleted_at = now
        await self.repository.update(hospital)
        
        # Soft delete user
        user_stmt = select(UserModel).where(UserModel.id == user_id)
        user = (await self.db.execute(user_stmt)).scalar_one_or_none()
        if user:
            user.deleted_at = now
            user.is_active = False
            
        await self.db.commit()
        logger.info("hospital_account_deleted", user_id=str(user_id))
