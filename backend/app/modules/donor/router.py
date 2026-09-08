# backend/app/modules/donor/router.py
# LifeLink AI — Donor Module Router
# Architecture Reference: ARCHITECTURE.md Section 33 & API.md Section 7

from __future__ import annotations

import datetime
import uuid
from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_active_user
from app.modules.auth.models import User
from app.modules.donor.schemas import (
    DonorAvailabilityToggleSchema,
    DonorCreateSchema,
    DonorOpportunityResponseCreateSchema,
    DonorResponseSchema,
    DonorUpdateSchema,
)
from app.modules.donor.service import DonorService

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
    summary="Create or register donor profile",
)
@router.post(
    "/profile",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def create_donor_profile(
    data: DonorCreateSchema,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = DonorService(db)
    donor = await service.create_or_update_profile(current_user.id, data)
    resp = DonorResponseSchema.model_validate(donor).model_dump(mode="json")
    return _format_success(data=resp, message="Donor profile saved successfully")


@router.get(
    "/me",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get current donor profile",
)
@router.get(
    "/profile",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
async def get_my_donor_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = DonorService(db)
    donor = await service.get_profile(current_user.id)
    resp = DonorResponseSchema.model_validate(donor).model_dump(mode="json")
    return _format_success(data=resp)


@router.put(
    "/me",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Update donor profile",
)
async def update_my_donor_profile(
    data: DonorUpdateSchema,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = DonorService(db)
    donor = await service.update_profile(current_user.id, data)
    resp = DonorResponseSchema.model_validate(donor).model_dump(mode="json")
    return _format_success(data=resp, message="Donor profile updated successfully")


@router.patch(
    "/me/availability",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Toggle donor emergency availability",
)
async def toggle_my_availability(
    data: DonorAvailabilityToggleSchema,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = DonorService(db)
    donor = await service.toggle_availability(current_user.id, data.is_available)
    resp = DonorResponseSchema.model_validate(donor).model_dump(mode="json")
    status_str = "Available for Emergencies" if donor.is_available else "Off Duty"
    return _format_success(data=resp, message=f"Availability updated to: {status_str}")


@router.get(
    "/me/dashboard",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get donor dashboard data, eligibility metrics, and compatible opportunities",
)
async def get_my_donor_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = DonorService(db)
    dashboard_data = await service.get_dashboard_data(current_user.id)
    return _format_success(data=dashboard_data, message="Donor dashboard retrieved")


@router.get(
    "/me/opportunities/{request_id}",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get compatible emergency opportunity details from donor perspective",
)
async def get_my_opportunity_detail(
    request_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = DonorService(db)
    detail = await service.get_opportunity_detail(current_user.id, request_id)
    return _format_success(data=detail, message="Opportunity details retrieved")


@router.post(
    "/me/opportunities/{request_id}/respond",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Respond to compatible emergency opportunity (ACCEPT or DECLINE)",
)
async def respond_to_my_opportunity(
    request_id: uuid.UUID,
    payload: DonorOpportunityResponseCreateSchema,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = DonorService(db)
    resp = await service.respond_to_opportunity(
        user_id=current_user.id,
        request_id=request_id,
        status=payload.status,
        notes=payload.notes,
    )
    return _format_success(data=resp, message=f"Emergency response registered: {payload.status}")


