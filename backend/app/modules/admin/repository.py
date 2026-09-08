# backend/app/modules/admin/repository.py
# LifeLink AI — Admin Module Repository Layer
# Architecture Reference: ARCHITECTURE.md Section 16 & Section 22

from __future__ import annotations

import uuid
from typing import Optional, Sequence

import structlog
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.blood_bank.models import BloodBank
from app.modules.hospital.models import Hospital

logger = structlog.get_logger(__name__)


class AdminRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_pending_hospitals(self) -> Sequence[Hospital]:
        stmt = (
            select(Hospital)
            .where(
                Hospital.is_verified == False,  # noqa: E712
                Hospital.is_active == True,  # noqa: E712
                Hospital.deleted_at == None,  # noqa: E711
            )
            .order_by(Hospital.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_pending_blood_banks(self) -> Sequence[BloodBank]:
        stmt = (
            select(BloodBank)
            .where(
                BloodBank.is_verified == False,  # noqa: E712
                BloodBank.is_active == True,  # noqa: E712
                BloodBank.deleted_at == None,  # noqa: E711
            )
            .order_by(BloodBank.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_hospital_by_id(self, hospital_id: uuid.UUID) -> Optional[Hospital]:
        stmt = select(Hospital).where(
            Hospital.id == hospital_id,
            Hospital.deleted_at == None,  # noqa: E711
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_blood_bank_by_id(self, blood_bank_id: uuid.UUID) -> Optional[BloodBank]:
        stmt = select(BloodBank).where(
            BloodBank.id == blood_bank_id,
            BloodBank.deleted_at == None,  # noqa: E711
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def set_hospital_verification(self, hospital: Hospital, is_verified: bool) -> Hospital:
        hospital.is_verified = is_verified
        await self.db.flush()
        return hospital

    async def set_blood_bank_verification(self, blood_bank: BloodBank, is_verified: bool) -> BloodBank:
        blood_bank.is_verified = is_verified
        await self.db.flush()
        return blood_bank

    async def list_all_hospitals(self, status: Optional[str] = None) -> Sequence[Hospital]:
        stmt = select(Hospital).where(Hospital.deleted_at.is_(None))
        if status:
            stmt = stmt.where(Hospital.status == status)
        stmt = stmt.order_by(Hospital.created_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def list_all_blood_banks(self, status: Optional[str] = None) -> Sequence[BloodBank]:
        stmt = select(BloodBank).where(BloodBank.deleted_at.is_(None))
        if status:
            stmt = stmt.where(BloodBank.status == status)
        stmt = stmt.order_by(BloodBank.created_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def set_hospital_status(self, hospital: Hospital, status: str) -> Hospital:
        hospital.status = status
        if status in ("SUSPENDED", "BLOCKED"):
            hospital.is_active = False
        else:
            hospital.is_active = True
        await self.db.flush()
        return hospital

    async def set_blood_bank_status(self, blood_bank: BloodBank, status: str) -> BloodBank:
        blood_bank.status = status
        if status in ("SUSPENDED", "BLOCKED"):
            blood_bank.is_active = False
        else:
            blood_bank.is_active = True
        await self.db.flush()
        return blood_bank

