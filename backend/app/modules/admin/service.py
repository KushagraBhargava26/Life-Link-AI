# backend/app/modules/admin/service.py
# LifeLink AI — Admin Module Service Layer
# Architecture Reference: ARCHITECTURE.md Section 16 & Section 22

from __future__ import annotations

import uuid

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.admin.exceptions import BloodBankNotFoundError, HospitalNotFoundError
from app.modules.admin.repository import AdminRepository
from app.modules.admin.schemas import (
    AdminFacilityListResponseSchema,
    PendingBloodBankSchema,
    PendingHospitalSchema,
    PendingVerificationsResponseSchema,
)

logger = structlog.get_logger(__name__)


class AdminService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = AdminRepository(db)

    def _hospital_to_schema(self, h: Any) -> PendingHospitalSchema:
        return PendingHospitalSchema(
            id=h.id,
            name=h.name,
            registration_number=h.registration_number,
            type=h.type.value if hasattr(h.type, "value") else str(h.type),
            city=h.city,
            state=h.state,
            phone=h.phone,
            email=h.email,
            license_issue_date=h.license_issue_date,
            license_expiry_date=h.license_expiry_date,
            certificate_url=h.certificate_url,
            status=h.status or "ACTIVE",
            is_verified=h.is_verified,
            created_at=h.created_at,
        )

    def _blood_bank_to_schema(self, bb: Any) -> PendingBloodBankSchema:
        return PendingBloodBankSchema(
            id=bb.id,
            name=bb.name,
            license_number=bb.license_number,
            city=bb.city,
            state=bb.state,
            phone=bb.phone,
            email=bb.email,
            is_24_hours=bb.is_24_hours,
            license_issue_date=bb.license_issue_date,
            license_expiry_date=bb.license_expiry_date,
            certificate_url=bb.certificate_url,
            status=bb.status or "ACTIVE",
            is_verified=bb.is_verified,
            created_at=bb.created_at,
        )

    async def get_pending_verifications(self) -> PendingVerificationsResponseSchema:
        hospitals = await self.repository.get_pending_hospitals()
        blood_banks = await self.repository.get_pending_blood_banks()

        h_schemas = [self._hospital_to_schema(h) for h in hospitals]
        bb_schemas = [self._blood_bank_to_schema(bb) for bb in blood_banks]

        return PendingVerificationsResponseSchema(
            hospitals=h_schemas,
            blood_banks=bb_schemas,
            total_pending=len(h_schemas) + len(bb_schemas),
        )

    async def get_all_facilities(self, status: Optional[str] = None) -> AdminFacilityListResponseSchema:
        hospitals = await self.repository.list_all_hospitals(status=status)
        blood_banks = await self.repository.list_all_blood_banks(status=status)

        h_schemas = [self._hospital_to_schema(h) for h in hospitals]
        bb_schemas = [self._blood_bank_to_schema(bb) for bb in blood_banks]

        all_facilities = list(hospitals) + list(blood_banks)
        total_active = sum(1 for f in all_facilities if getattr(f, "status", "ACTIVE") == "ACTIVE")
        total_suspended = sum(1 for f in all_facilities if getattr(f, "status", "ACTIVE") == "SUSPENDED")
        total_blocked = sum(1 for f in all_facilities if getattr(f, "status", "ACTIVE") == "BLOCKED")

        return AdminFacilityListResponseSchema(
            hospitals=h_schemas,
            blood_banks=bb_schemas,
            total_active=total_active,
            total_suspended=total_suspended,
            total_blocked=total_blocked,
        )

    async def verify_hospital(self, hospital_id: uuid.UUID, is_verified: bool = True) -> PendingHospitalSchema:
        hospital = await self.repository.get_hospital_by_id(hospital_id)
        if not hospital:
            raise HospitalNotFoundError(str(hospital_id))

        updated = await self.repository.set_hospital_verification(hospital, is_verified)
        await self.db.commit()
        await self.db.refresh(updated)
        logger.info("hospital_verification_updated", hospital_id=str(hospital_id), is_verified=is_verified)
        return self._hospital_to_schema(updated)

    async def verify_blood_bank(self, blood_bank_id: uuid.UUID, is_verified: bool = True) -> PendingBloodBankSchema:
        blood_bank = await self.repository.get_blood_bank_by_id(blood_bank_id)
        if not blood_bank:
            raise BloodBankNotFoundError(str(blood_bank_id))

        updated = await self.repository.set_blood_bank_verification(blood_bank, is_verified)
        await self.db.commit()
        await self.db.refresh(updated)
        logger.info("blood_bank_verification_updated", blood_bank_id=str(blood_bank_id), is_verified=is_verified)
        return self._blood_bank_to_schema(updated)

    async def set_hospital_status(self, hospital_id: uuid.UUID, status: str) -> PendingHospitalSchema:
        hospital = await self.repository.get_hospital_by_id(hospital_id)
        if not hospital:
            raise HospitalNotFoundError(str(hospital_id))

        updated = await self.repository.set_hospital_status(hospital, status)
        await self.db.commit()
        await self.db.refresh(updated)
        logger.info("hospital_status_updated", hospital_id=str(hospital_id), status=status)
        return self._hospital_to_schema(updated)

    async def set_blood_bank_status(self, blood_bank_id: uuid.UUID, status: str) -> PendingBloodBankSchema:
        blood_bank = await self.repository.get_blood_bank_by_id(blood_bank_id)
        if not blood_bank:
            raise BloodBankNotFoundError(str(blood_bank_id))

        updated = await self.repository.set_blood_bank_status(blood_bank, status)
        await self.db.commit()
        await self.db.refresh(updated)
        logger.info("blood_bank_status_updated", blood_bank_id=str(blood_bank_id), status=status)
        return self._blood_bank_to_schema(updated)

