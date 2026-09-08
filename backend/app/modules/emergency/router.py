# backend/app/modules/emergency/router.py
# LifeLink AI — Emergency Module Router
# Architecture Reference: ARCHITECTURE.md Section 22 (Module Breakdown)
#
# Rule: Router contains FastAPI route definitions ONLY — no business logic.
# All business logic must be delegated to emergency.service
#
# Phase 1.1: Empty router — no endpoints implemented.
# Phase 1.2+: Add endpoint definitions here.

from __future__ import annotations

import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.emergency.schemas import (
    EmergencyPublicTrackingSchema,
    EmergencyRequestCreateSchema,
    EmergencyRequestResponseSchema,
    EmergencyStatusResponseSchema,
    EmergencyStatusUpdateSchema,
)
from app.modules.emergency.service import EmergencyService

router = APIRouter()


def _format_success(data: Any, message: str = "Operation successful") -> dict[str, Any]:
    return {
        "success": True,
        "data": data,
        "message": message,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


@router.post(
    "",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Create Emergency Blood Request",
    description="Zero-barrier public intake for emergency blood requests.",
)
@router.post(
    "/requests",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def create_emergency_request(
    payload: EmergencyRequestCreateSchema,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = EmergencyService(db)
    created = await service.create_request(payload)
    resp_data = EmergencyRequestResponseSchema.model_validate(created).model_dump(mode="json")
    return _format_success(
        data=resp_data,
        message=f"Emergency request {created.request_number} submitted successfully. Initial status: {created.status}",
    )


@router.get(
    "/{request_id}",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get Emergency Request Details",
    description="Retrieve emergency request by UUID or request number (e.g. EMR-2026-0001).",
)
@router.get(
    "/requests/{request_id}",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def get_emergency_request(
    request_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = EmergencyService(db)
    req = await service.get_request(request_id)
    resp_data = EmergencyPublicTrackingSchema.model_validate(req).model_dump(mode="json")
    return _format_success(data=resp_data)


@router.get(
    "/{request_id}/status",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get Emergency Request Status",
    description="Lightweight status check for real-time tracking polling.",
)
@router.get(
    "/requests/{request_id}/status",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def get_emergency_status(
    request_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = EmergencyService(db)
    req = await service.get_request(request_id)
    resp_data = EmergencyStatusResponseSchema.model_validate(req).model_dump(mode="json")
    return _format_success(data=resp_data)


@router.patch(
    "/{request_id}/status",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Update Emergency Request Status",
)
@router.patch(
    "/requests/{request_id}/status",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def update_emergency_status(
    request_id: str,
    payload: EmergencyStatusUpdateSchema,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = EmergencyService(db)
    req = await service.update_status(
        identifier=request_id,
        new_status=payload.status,
        cancellation_reason=payload.cancellation_reason,
        notes=payload.notes,
    )
    resp_data = EmergencyStatusResponseSchema.model_validate(req).model_dump(mode="json")
    return _format_success(data=resp_data, message=f"Emergency status updated to {req.status}")


@router.post(
    "/{request_id}/cancel",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Cancel Emergency Request",
)
@router.post(
    "/requests/{request_id}/cancel",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def cancel_emergency_request(
    request_id: str,
    reason: Optional[str] = Query(None, description="Cancellation reason"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = EmergencyService(db)
    req = await service.update_status(
        identifier=request_id,
        new_status="CANCELLED",
        cancellation_reason=reason or "Cancelled by user/hospital",
    )
    resp_data = EmergencyStatusResponseSchema.model_validate(req).model_dump(mode="json")
    return _format_success(data=resp_data, message="Emergency request cancelled successfully")


@router.post(
    "/{request_id}/fulfill",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Fulfill Emergency Request",
)
@router.post(
    "/requests/{request_id}/fulfill",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def fulfill_emergency_request(
    request_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = EmergencyService(db)
    req = await service.update_status(
        identifier=request_id,
        new_status="FULFILLED",
    )
    resp_data = EmergencyStatusResponseSchema.model_validate(req).model_dump(mode="json")
    return _format_success(data=resp_data, message="Emergency request fulfilled successfully")


@router.get(
    "",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="List Emergency Requests",
)
@router.get(
    "/requests",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def list_emergency_requests(
    status: Optional[str] = Query(None, description="Filter by status (e.g. PENDING)"),
    blood_type: Optional[str] = Query(None, description="Filter by blood type (e.g. O-)"),
    city: Optional[str] = Query(None, description="Filter by city"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = EmergencyService(db)
    items, total = await service.list_requests(
        status=status,
        blood_type=blood_type,
        city=city,
        limit=limit,
        offset=offset,
    )
    serialized = [
        EmergencyPublicTrackingSchema.model_validate(item).model_dump(mode="json")
        for item in items
    ]
    return {
        "success": True,
        "data": serialized,
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_next": offset + limit < total,
            "has_previous": offset > 0,
        },
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
