# backend/app/modules/donor/repository.py
# LifeLink AI — Donor Module Repository Layer
# Architecture Reference: ARCHITECTURE.md Section 16 & DATABASE.md Section 6

from __future__ import annotations

import uuid
from typing import Optional

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.donor.models import Donor

logger = structlog.get_logger(__name__)


class DonorRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_user_id(self, user_id: uuid.UUID) -> Optional[Donor]:
        stmt = (
            select(Donor)
            .where(
                Donor.user_id == user_id,
                Donor.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, donor_id: uuid.UUID) -> Optional[Donor]:
        stmt = (
            select(Donor)
            .where(
                Donor.id == donor_id,
                Donor.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, donor: Donor) -> Donor:
        self.db.add(donor)
        await self.db.flush()
        return donor

    async def update(self, donor: Donor) -> Donor:
        await self.db.flush()
        return donor
