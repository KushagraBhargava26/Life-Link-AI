"""Matching module FastAPI router.
Exposes authenticated matching execution, match history, and candidate status updates.
Enforces hospital ReBAC authorization and strict Zero-PII sanitization.
"""

from __future__ import annotations
import uuid
from typing import Optional, Set
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.dependencies import get_current_active_user
from app.core.exceptions import NotFoundError, ForbiddenError
from app.modules.auth.models import User
from app.modules.hospital.models import Hospital, HospitalStaff
from app.modules.hospital.repository import HospitalRepository
from app.modules.emergency.models import EmergencyRequest
from app.modules.matching.service import MatchingService
from app.modules.matching.schemas import (
    MatchRunResponseSchema,
    MatchCandidateResponseSchema,
    CandidateStatusUpdateSchema,
)

router = APIRouter()


async def _verify_hospital_request_access(
    request_id: uuid.UUID,
    user: User,
    db: AsyncSession,
) -> EmergencyRequest:
    """ReBAC check: Ensures caller is authorized to view or match this emergency request."""
    stmt = select(EmergencyRequest).where(
        EmergencyRequest.id == request_id,
        EmergencyRequest.deleted_at.is_(None),
    )
    res = await db.execute(stmt)
    req = res.scalar_one_or_none()
    if not req:
        raise NotFoundError(f"Emergency request {request_id} not found")

    user_roles: Set[str] = {r.role.upper() for r in user.roles} if user.roles else set()

    # Platform admin / Super admin has full operational access
    if "SUPER_ADMIN" in user_roles or "ADMIN" in user_roles:
        return req

    # Requester user
    if req.requested_by and req.requested_by == user.id:
        return req

    # Hospital clinician / staff ownership
    if req.hospital_id:
        # Check direct hospital staff mapping
        staff_stmt = select(HospitalStaff).where(
            HospitalStaff.hospital_id == req.hospital_id,
            HospitalStaff.user_id == user.id,
            HospitalStaff.deleted_at.is_(None),
        )
        staff_res = await db.execute(staff_stmt)
        if staff_res.scalar_one_or_none():
            return req

        # Check hospital creator ownership
        hosp_stmt = select(Hospital).where(
            Hospital.id == req.hospital_id,
            Hospital.created_by == user.id,
            Hospital.deleted_at.is_(None),
        )
        hosp_res = await db.execute(hosp_stmt)
        if hosp_res.scalar_one_or_none():
            return req

    raise ForbiddenError("You are not authorized to access matching for this emergency request")


@router.post(
    "/requests/{id}/match",
    status_code=status.HTTP_200_OK,
    summary="Execute or re-run AI matching for an emergency request",
)
@router.post(
    "/{id}/match",
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def run_matching(
    id: uuid.UUID,
    search_radius_km: float = 50.0,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Discovers, deterministically filters, and ranks compatible blood supply candidates.
    Integrates the AI response propensity model with automatic deterministic fallback.
    """
    await _verify_hospital_request_access(id, current_user, db)

    service = MatchingService(db)
    run_result = await service.execute_matching(
        emergency_request_id=id,
        user_id=current_user.id,
        search_radius_km=search_radius_km,
    )

    return {
        "success": True,
        "data": run_result,
        "message": f"Matching executed successfully ({len(run_result.blood_banks)} blood banks, {len(run_result.donors)} donors)",
    }


@router.get(
    "/requests/{id}/matches",
    status_code=status.HTTP_200_OK,
    summary="Get latest matching recommendations for an emergency request",
)
@router.get(
    "/{id}/matches",
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def get_matches(
    id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves the most recent match run results for the emergency request."""
    await _verify_hospital_request_access(id, current_user, db)

    service = MatchingService(db)
    run_result = await service.get_matches_for_request(id)

    if not run_result:
        # If no match run was executed yet, execute initial run automatically
        run_result = await service.execute_matching(
            emergency_request_id=id,
            user_id=current_user.id,
            search_radius_km=50.0,
        )

    return {
        "success": True,
        "data": run_result,
        "message": "Match results retrieved",
    }


@router.patch(
    "/requests/{id}/matches/{candidate_id}",
    status_code=status.HTTP_200_OK,
    summary="Update candidate status (SHORTLISTED, DISMISSED)",
)
@router.patch(
    "/{id}/matches/{candidate_id}",
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def update_candidate_status(
    id: uuid.UUID,
    candidate_id: uuid.UUID,
    payload: CandidateStatusUpdateSchema,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Updates candidate operational status (e.g. SHORTLISTED or DISMISSED)."""
    await _verify_hospital_request_access(id, current_user, db)

    service = MatchingService(db)
    updated = await service.update_candidate_status(candidate_id, payload.status)

    return {
        "success": True,
        "data": updated,
        "message": f"Candidate status updated to {payload.status}",
    }
