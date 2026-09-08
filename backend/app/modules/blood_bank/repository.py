# backend/app/modules/blood_bank/repository.py
# LifeLink AI — Blood Bank Module Database Repository
# Architecture Reference: ARCHITECTURE.md Section 27; DATABASE.md Section 8

from __future__ import annotations

import uuid
from typing import Optional

import structlog
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.blood_bank.models import BloodBank
from app.modules.emergency.models import EmergencyRequest, EmergencyStatusEnum

logger = structlog.get_logger(__name__)


class BloodBankRepository:
    """Async repository for BloodBank entity database operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, blood_bank: BloodBank) -> BloodBank:
        self.db.add(blood_bank)
        await self.db.flush()
        await self.db.refresh(blood_bank)
        return blood_bank

    async def get_by_id(self, blood_bank_id: uuid.UUID) -> Optional[BloodBank]:
        stmt = select(BloodBank).where(
            BloodBank.id == blood_bank_id,
            BloodBank.deleted_at.is_(None),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_license_number(self, license_number: str) -> Optional[BloodBank]:
        stmt = select(BloodBank).where(
            BloodBank.license_number == license_number,
            BloodBank.deleted_at.is_(None),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: uuid.UUID) -> Optional[BloodBank]:
        """Find blood bank managed or created by user."""
        stmt = select(BloodBank).where(
            or_(
                BloodBank.manager_user_id == user_id,
                BloodBank.created_by == user_id,
            ),
            BloodBank.deleted_at.is_(None),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, blood_bank: BloodBank) -> BloodBank:
        await self.db.flush()
        await self.db.refresh(blood_bank)
        return blood_bank

    async def list_blood_banks(
        self,
        city: Optional[str] = None,
        is_24_hours: Optional[bool] = None,
        is_verified: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[BloodBank], int]:
        stmt = select(BloodBank).where(BloodBank.deleted_at.is_(None), BloodBank.is_active.is_(True))
        if city:
            stmt = stmt.where(BloodBank.city.ilike(f"%{city}%"))
        if is_24_hours is not None:
            stmt = stmt.where(BloodBank.is_24_hours == is_24_hours)
        if is_verified is not None:
            stmt = stmt.where(BloodBank.is_verified == is_verified)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.db.execute(count_stmt)).scalar_one()

        stmt = stmt.order_by(BloodBank.name.asc()).offset(offset).limit(limit)
        items = (await self.db.execute(stmt)).scalars().all()
        return list(items), total

    async def get_emergency_demand_in_city(
        self,
        city: str,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[EmergencyRequest], int]:
        """Retrieve active emergency requests requiring blood in the city or surrounding area."""
        active_statuses = [
            EmergencyStatusEnum.PENDING.value,
            EmergencyStatusEnum.MATCHING.value,
            EmergencyStatusEnum.NOTIFIED.value,
            EmergencyStatusEnum.CONFIRMED.value,
            EmergencyStatusEnum.IN_PROGRESS.value,
        ]
        stmt = select(EmergencyRequest).where(
            EmergencyRequest.deleted_at.is_(None),
            EmergencyRequest.status.in_(active_statuses),
        )
        if city:
            stmt = stmt.where(EmergencyRequest.city.ilike(f"%{city}%"))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.db.execute(count_stmt)).scalar_one()

        stmt = stmt.order_by(EmergencyRequest.created_at.desc()).offset(offset).limit(limit)
        items = (await self.db.execute(stmt)).scalars().all()
        return list(items), total
