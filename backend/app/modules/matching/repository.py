"""Matching module database access layer."""

from __future__ import annotations
import uuid
from typing import Optional, List
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.matching.models import (
    MatchRun,
    MatchCandidate,
    MatchRunStatusEnum,
    MatchCandidateStatusEnum,
)


class MatchingRepository:
    """Async repository for matching runs and candidates."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_next_run_number(self, emergency_request_id: uuid.UUID) -> int:
        """Returns the next sequential run number for the emergency request."""
        stmt = select(func.coalesce(func.max(MatchRun.run_number), 0)).where(
            MatchRun.emergency_request_id == emergency_request_id
        )
        res = await self.db.execute(stmt)
        return int(res.scalar_one()) + 1

    async def create_match_run(self, run: MatchRun) -> MatchRun:
        """Persists a new match run."""
        self.db.add(run)
        await self.db.flush()
        return run

    async def create_candidates(self, candidates: List[MatchCandidate]) -> List[MatchCandidate]:
        """Bulk persists match candidates."""
        self.db.add_all(candidates)
        await self.db.flush()
        return candidates

    async def get_latest_run_for_request(self, emergency_request_id: uuid.UUID) -> Optional[MatchRun]:
        """Retrieves the most recent match run for an emergency request."""
        stmt = (
            select(MatchRun)
            .where(
                MatchRun.emergency_request_id == emergency_request_id,
                MatchRun.deleted_at.is_(None),
            )
            .options(selectinload(MatchRun.candidates))
            .order_by(MatchRun.run_number.desc())
            .limit(1)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_candidate_by_id(self, candidate_id: uuid.UUID) -> Optional[MatchCandidate]:
        """Retrieves a single candidate by ID."""
        stmt = select(MatchCandidate).where(
            MatchCandidate.id == candidate_id,
            MatchCandidate.deleted_at.is_(None),
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def update_candidate_status(
        self,
        candidate_id: uuid.UUID,
        new_status: MatchCandidateStatusEnum,
    ) -> Optional[MatchCandidate]:
        """Updates the operational status of a candidate."""
        cand = await self.get_candidate_by_id(candidate_id)
        if cand:
            cand.status = new_status
            await self.db.flush()
        return cand
