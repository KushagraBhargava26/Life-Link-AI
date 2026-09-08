# backend/app/modules/emergency/repository.py
# LifeLink AI — Emergency Module Repository Layer
# Architecture Reference: ARCHITECTURE.md Section 16 (Backend Architecture)
#
# Rule: Repository contains DATABASE QUERIES ONLY — no business logic.
# - Imports ONLY from: same module's models.py
# - FORBIDDEN: importing anything outside its own module
#
# Phase 1.1: Empty repository — no queries implemented.
# Phase 1.2+: Implement SQLAlchemy async queries here.

from __future__ import annotations

import uuid
from typing import Optional, Sequence

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.emergency.models import EmergencyRequest

logger = structlog.get_logger(__name__)


class EmergencyRepository:
    """
    Database queries for emergency requests.
    Rule: Repository contains queries only — no business logic.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, emergency_request: EmergencyRequest) -> EmergencyRequest:
        self.db.add(emergency_request)
        await self.db.flush()
        await self.db.refresh(emergency_request)
        return emergency_request

    async def get_by_id(self, request_id: uuid.UUID) -> Optional[EmergencyRequest]:
        stmt = select(EmergencyRequest).where(
            EmergencyRequest.id == request_id,
            EmergencyRequest.deleted_at.is_(None),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_request_number(self, request_number: str) -> Optional[EmergencyRequest]:
        stmt = select(EmergencyRequest).where(
            EmergencyRequest.request_number == request_number,
            EmergencyRequest.deleted_at.is_(None),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_count_for_year(self, year: int) -> int:
        import datetime
        start_date = datetime.datetime(year, 1, 1, tzinfo=datetime.timezone.utc)
        end_date = datetime.datetime(year + 1, 1, 1, tzinfo=datetime.timezone.utc)
        stmt = (
            select(func.count())
            .select_from(EmergencyRequest)
            .where(
                EmergencyRequest.created_at >= start_date,
                EmergencyRequest.created_at < end_date,
            )
        )
        result = await self.db.execute(stmt)
        count = result.scalar() or 0
        return int(count)

    async def list_requests(
        self,
        status: Optional[str] = None,
        blood_type: Optional[str] = None,
        city: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[Sequence[EmergencyRequest], int]:
        base_stmt = select(EmergencyRequest).where(EmergencyRequest.deleted_at.is_(None))

        if status:
            base_stmt = base_stmt.where(EmergencyRequest.status == status)
        if blood_type:
            base_stmt = base_stmt.where(EmergencyRequest.blood_type == blood_type)
        if city:
            base_stmt = base_stmt.where(EmergencyRequest.city.ilike(f"%{city}%"))

        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = (await self.db.execute(count_stmt)).scalar() or 0

        paginated_stmt = (
            base_stmt.order_by(EmergencyRequest.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(paginated_stmt)
        items = result.scalars().all()

        return items, int(total)

    async def update(self, emergency_request: EmergencyRequest) -> EmergencyRequest:
        await self.db.flush()
        await self.db.refresh(emergency_request)
        return emergency_request
