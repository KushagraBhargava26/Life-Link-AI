# backend/app/modules/hospital/router.py
# LifeLink AI — Hospital Module API Router
# Architecture Reference: ARCHITECTURE.md Section 27; API.md Section 8

from __future__ import annotations

import uuid
from typing import Any, Optional

import structlog
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationError
from app.database import get_db
from app.dependencies import get_current_active_user, get_pagination, require_role
from app.modules.auth.models import User
from app.modules.emergency.schemas import (
    EmergencyRequestCreateSchema,
    EmergencyRequestResponseSchema,
)
from app.modules.hospital.schemas import (
    HospitalCreateSchema,
    HospitalDashboardSchema,
    HospitalResponseSchema,
    HospitalUpdateSchema,
)
from app.modules.hospital.service import HospitalService

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post(
    "",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Register Hospital Facility Profile",
)
async def create_hospital_profile(
    data: HospitalCreateSchema,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Register a new hospital profile. Links calling user as primary hospital admin."""
    service = HospitalService(db)
    hospital = await service.create_profile(data, current_user.id)
    return {
        "success": True,
        "message": "Hospital facility profile created successfully",
        "data": HospitalResponseSchema.model_validate(hospital).model_dump(),
    }


@router.get(
    "/me",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get Own Hospital Profile",
)
async def get_my_hospital(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Retrieve hospital profile associated with authenticated user."""
    service = HospitalService(db)
    hospital = await service.get_my_hospital(current_user.id)
    return {
        "success": True,
        "data": HospitalResponseSchema.model_validate(hospital).model_dump(),
    }


@router.put(
    "/me",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Update Own Hospital Profile",
)
async def update_my_hospital(
    data: HospitalUpdateSchema,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Update hospital facility profile."""
    service = HospitalService(db)
    hospital = await service.update_my_hospital(data, current_user.id)
    return {
        "success": True,
        "message": "Hospital profile updated successfully",
        "data": HospitalResponseSchema.model_validate(hospital).model_dump(),
    }


@router.get(
    "/me/dashboard",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get Hospital Dashboard Data",
)
async def get_hospital_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get live operational dashboard metrics and active requisitions."""
    service = HospitalService(db)
    dashboard_data = await service.get_hospital_dashboard(current_user.id)
    return {
        "success": True,
        "data": {
            "hospital": HospitalResponseSchema.model_validate(dashboard_data["hospital"]).model_dump(),
            "active_requests_count": dashboard_data["active_requests_count"],
            "pending_requests_count": dashboard_data["pending_requests_count"],
            "recent_requests": dashboard_data["recent_requests"],
        },
    }


@router.get(
    "/me/requests",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="List Hospital Emergency Requests",
)
async def list_hospital_requests(
    current_user: User = Depends(get_current_active_user),
    pagination: dict[str, int] = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """List all emergency requisitions associated with this hospital."""
    service = HospitalService(db)
    items, total = await service.list_hospital_requests(
        current_user.id, limit=pagination["limit"], offset=pagination["offset"]
    )
    return {
        "success": True,
        "data": {
            "items": items,
            "total": total,
            "limit": pagination["limit"],
            "offset": pagination["offset"],
        },
    }


@router.post(
    "/me/requests",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Create Hospital Emergency Requisition",
)
async def create_hospital_emergency_request(
    data: EmergencyRequestCreateSchema,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Submit a real emergency blood requisition from this hospital."""
    service = HospitalService(db)
    req = await service.create_hospital_emergency_request(data, current_user.id)
    return {
        "success": True,
        "message": "Emergency requisition dispatched successfully",
        "data": {
            "id": str(req.id),
            "request_number": req.request_number,
            "blood_type": req.blood_type,
            "units_required": req.units_required,
            "urgency_level": req.urgency_level,
            "status": req.status,
            "hospital_name": req.hospital_name,
            "city": req.city,
            "created_at": req.created_at.isoformat() if req.created_at else None,
        },
    }


@router.get(
    "",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="List Hospitals Directory",
)
async def list_hospitals(
    city: Optional[str] = Query(None, description="Filter by city"),
    is_verified: Optional[bool] = Query(None, description="Filter by verification status"),
    has_blood_bank: Optional[bool] = Query(None, description="Filter by blood bank availability"),
    pagination: dict[str, int] = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Public authenticated directory of hospitals."""
    service = HospitalService(db)
    items, total = await service.list_hospitals(
        city=city,
        is_verified=is_verified,
        has_blood_bank=has_blood_bank,
        limit=pagination["limit"],
        offset=pagination["offset"],
    )
    return {
        "success": True,
        "data": {
            "items": [HospitalResponseSchema.model_validate(h).model_dump() for h in items],
            "total": total,
            "limit": pagination["limit"],
            "offset": pagination["offset"],
        },
    }


@router.get(
    "/{hospital_id}",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get Hospital Details by ID",
)
async def get_hospital_by_id(
    hospital_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get public facility profile of a specific hospital."""
    service = HospitalService(db)
    hospital = await service.get_hospital_by_id(hospital_id)
    return {
        "success": True,
        "data": HospitalResponseSchema.model_validate(hospital).model_dump(),
    }

@router.delete(
    "/me",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Soft-delete hospital account",
)
async def delete_my_hospital_account(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = HospitalService(db)
    await service.delete_account(current_user.id)
    return {"success": True, "message": "Hospital account deleted."}
