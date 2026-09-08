# backend/app/modules/hospital/repository.py
# LifeLink AI — Hospital Module Database Repository
# Architecture Reference: ARCHITECTURE.md Section 27; DATABASE.md Section 7

from __future__ import annotations

import uuid
from typing import Optional

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.emergency.models import EmergencyRequest
from app.modules.hospital.models import Hospital, HospitalStaff

logger = structlog.get_logger(__name__)


class HospitalRepository:
    """Async repository for Hospital entity database operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, hospital: Hospital) -> Hospital:
        self.db.add(hospital)
        await self.db.flush()
        await self.db.refresh(hospital)
        return hospital

    async def get_by_id(self, hospital_id: uuid.UUID) -> Optional[Hospital]:
        stmt = (
            select(Hospital)
            .where(
                Hospital.id == hospital_id,
                Hospital.deleted_at.is_(None),
            )
            .options(selectinload(Hospital.staff))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_registration_number(self, reg_num: str) -> Optional[Hospital]:
        stmt = select(Hospital).where(
            Hospital.registration_number == reg_num,
            Hospital.deleted_at.is_(None),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: uuid.UUID) -> Optional[Hospital]:
        """
        Find hospital associated with user: either as creator or assigned hospital staff.
        """
        # Check staff assignment first
        staff_stmt = select(HospitalStaff).where(
            HospitalStaff.user_id == user_id,
            HospitalStaff.deleted_at.is_(None),
        )
        staff_res = await self.db.execute(staff_stmt)
        staff_record = staff_res.scalar_one_or_none()
        if staff_record:
            return await self.get_by_id(staff_record.hospital_id)

        # Fallback to created_by
        creator_stmt = (
            select(Hospital)
            .where(
                Hospital.created_by == user_id,
                Hospital.deleted_at.is_(None),
            )
            .options(selectinload(Hospital.staff))
        )
        creator_res = await self.db.execute(creator_stmt)
        return creator_res.scalar_one_or_none()

    async def update(self, hospital: Hospital) -> Hospital:
        await self.db.flush()
        await self.db.refresh(hospital)
        return hospital

    async def list_hospitals(
        self,
        city: Optional[str] = None,
        is_verified: Optional[bool] = None,
        has_blood_bank: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Hospital], int]:
        stmt = select(Hospital).where(Hospital.deleted_at.is_(None), Hospital.is_active.is_(True))
        if city:
            stmt = stmt.where(Hospital.city.ilike(f"%{city}%"))
        if is_verified is not None:
            stmt = stmt.where(Hospital.is_verified == is_verified)
        if has_blood_bank is not None:
            stmt = stmt.where(Hospital.has_blood_bank == has_blood_bank)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.db.execute(count_stmt)).scalar_one()

        stmt = stmt.order_by(Hospital.name.asc()).offset(offset).limit(limit)
        items = (await self.db.execute(stmt)).scalars().all()
        return list(items), total

    async def add_staff(self, staff: HospitalStaff) -> HospitalStaff:
        self.db.add(staff)
        await self.db.flush()
        await self.db.refresh(staff)
        return staff

    async def get_staff(self, hospital_id: uuid.UUID, user_id: uuid.UUID) -> Optional[HospitalStaff]:
        stmt = select(HospitalStaff).where(
            HospitalStaff.hospital_id == hospital_id,
            HospitalStaff.user_id == user_id,
            HospitalStaff.deleted_at.is_(None),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_hospital_requests(
        self,
        hospital_id: uuid.UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[EmergencyRequest], int]:
        stmt = select(EmergencyRequest).where(
            EmergencyRequest.hospital_id == hospital_id,
            EmergencyRequest.deleted_at.is_(None),
        )
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.db.execute(count_stmt)).scalar_one()

        stmt = stmt.order_by(EmergencyRequest.created_at.desc()).offset(offset).limit(limit)
        items = (await self.db.execute(stmt)).scalars().all()
        return list(items), total
