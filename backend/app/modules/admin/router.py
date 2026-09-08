# backend/app/modules/admin/router.py
# LifeLink AI — Admin Module Router
# Architecture Reference: ARCHITECTURE.md Section 22 & API.md

from __future__ import annotations

import datetime
import uuid
from typing import Any, Optional

import structlog
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_admin
from app.modules.admin.schemas import (
    AdminFacilityListResponseSchema,
    FacilityStatusUpdateSchema,
    PendingBloodBankSchema,
    PendingHospitalSchema,
    PendingVerificationsResponseSchema,
    VerificationUpdateSchema,
)
from app.modules.admin.service import AdminService
from app.modules.auth.models import User

logger = structlog.get_logger(__name__)

router = APIRouter()


def _format_success(data: Any, message: str = "Operation successful") -> dict[str, Any]:
    return {
        "success": True,
        "data": data,
        "message": message,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


@router.get(
    "/verifications/pending",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="List all hospitals and blood banks awaiting verification",
)
async def get_pending_verifications(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = AdminService(db)
    pending = await service.get_pending_verifications()
    return _format_success(
        data=pending.model_dump(mode="json"),
        message="Pending verifications retrieved",
    )


@router.patch(
    "/hospitals/{hospital_id}/verify",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Verify or unverify a hospital",
)
async def verify_hospital(
    hospital_id: uuid.UUID,
    payload: VerificationUpdateSchema = VerificationUpdateSchema(is_verified=True),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = AdminService(db)
    updated = await service.verify_hospital(hospital_id, payload.is_verified)
    action = "verified" if payload.is_verified else "unverified"
    return _format_success(
        data=updated.model_dump(mode="json"),
        message=f"Hospital {updated.name} {action} successfully",
    )


@router.patch(
    "/blood-banks/{blood_bank_id}/verify",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Verify or unverify a blood bank",
)
async def verify_blood_bank(
    blood_bank_id: uuid.UUID,
    payload: VerificationUpdateSchema = VerificationUpdateSchema(is_verified=True),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = AdminService(db)
    updated = await service.verify_blood_bank(blood_bank_id, payload.is_verified)
    action = "verified" if payload.is_verified else "unverified"
    return _format_success(
        data=updated.model_dump(mode="json"),
        message=f"Blood bank {updated.name} {action} successfully",
    )


@router.get(
    "/facilities",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="List all registered facilities (hospitals & blood banks)",
)
async def get_all_facilities(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (ACTIVE, SUSPENDED, BLOCKED)"),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = AdminService(db)
    data = await service.get_all_facilities(status=status_filter)
    return _format_success(
        data=data.model_dump(mode="json"),
        message="Facilities retrieved successfully",
    )


@router.patch(
    "/hospitals/{hospital_id}/status",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Update hospital status (ACTIVE, SUSPENDED, BLOCKED)",
)
async def set_hospital_status(
    hospital_id: uuid.UUID,
    payload: FacilityStatusUpdateSchema,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = AdminService(db)
    updated = await service.set_hospital_status(hospital_id, payload.status)
    return _format_success(
        data=updated.model_dump(mode="json"),
        message=f"Hospital {updated.name} status updated to {updated.status}",
    )


@router.patch(
    "/blood-banks/{blood_bank_id}/status",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Update blood bank status (ACTIVE, SUSPENDED, BLOCKED)",
)
async def set_blood_bank_status(
    blood_bank_id: uuid.UUID,
    payload: FacilityStatusUpdateSchema,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = AdminService(db)
    updated = await service.set_blood_bank_status(blood_bank_id, payload.status)
    return _format_success(
        data=updated.model_dump(mode="json"),
        message=f"Blood bank {updated.name} status updated to {updated.status}",
    )

