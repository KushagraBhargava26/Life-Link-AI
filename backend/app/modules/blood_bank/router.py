# backend/app/modules/blood_bank/router.py
# LifeLink AI — Blood Bank Module API Router
# Architecture Reference: ARCHITECTURE.md Section 27; API.md Section 9

from __future__ import annotations

import uuid
from typing import Any, Optional

import structlog
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_active_user, get_pagination
from app.modules.auth.models import User
from app.modules.blood_bank.schemas import (
    BloodBankCreateSchema,
    BloodBankDashboardSchema,
    BloodBankResponseSchema,
    BloodBankUpdateSchema,
)
from app.modules.blood_bank.service import BloodBankService
from app.modules.inventory.schemas import BloodBankEmergencyRespondRequestSchema
from app.modules.inventory.service import InventoryService

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post(
    "",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Register Blood Bank Profile",
)
async def create_blood_bank_profile(
    data: BloodBankCreateSchema,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Register a new blood bank facility. Links calling user as managing administrator."""
    service = BloodBankService(db)
    bank = await service.create_profile(data, current_user.id)
    return {
        "success": True,
        "message": "Blood bank facility profile created successfully",
        "data": BloodBankResponseSchema.model_validate(bank).model_dump(),
    }


@router.get(
    "/me",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get Own Blood Bank Profile",
)
async def get_my_blood_bank(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Retrieve blood bank profile associated with authenticated user."""
    service = BloodBankService(db)
    bank = await service.get_my_blood_bank(current_user.id)
    return {
        "success": True,
        "data": BloodBankResponseSchema.model_validate(bank).model_dump(),
    }


@router.put(
    "/me",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Update Own Blood Bank Profile",
)
async def update_my_blood_bank(
    data: BloodBankUpdateSchema,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Update blood bank facility profile."""
    service = BloodBankService(db)
    bank = await service.update_my_blood_bank(data, current_user.id)
    return {
        "success": True,
        "message": "Blood bank profile updated successfully",
        "data": BloodBankResponseSchema.model_validate(bank).model_dump(),
    }


@router.get(
    "/me/dashboard",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get Blood Bank Dashboard Data",
)
async def get_blood_bank_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get live operational dashboard metrics and emergency demand visibility."""
    service = BloodBankService(db)
    dashboard_data = await service.get_blood_bank_dashboard(current_user.id)
    return {
        "success": True,
        "data": {
            "blood_bank": BloodBankResponseSchema.model_validate(dashboard_data["blood_bank"]).model_dump(),
            "active_emergency_demand_count": dashboard_data["active_emergency_demand_count"],
            "is_operational": dashboard_data["is_operational"],
            "emergency_demand": dashboard_data["emergency_demand"],
        },
    }


@router.get(
    "/me/demand",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="View Local Emergency Demand",
)
async def get_emergency_demand(
    current_user: User = Depends(get_current_active_user),
    pagination: dict[str, int] = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """View active emergency requisitions in the blood bank's jurisdiction (zero PII)."""
    service = BloodBankService(db)
    items, total = await service.get_emergency_demand(
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


@router.get(
    "/me/demand/{request_id}/availability",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Check Availability for Emergency Requisition",
)
async def check_demand_availability(
    request_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Check deterministic stock availability for a specific emergency requisition."""
    bb_service = BloodBankService(db)
    bank = await bb_service.get_my_blood_bank(current_user.id)
    inv_service = InventoryService(db)
    data = await inv_service.check_demand_availability(
        facility_type="BLOOD_BANK",
        facility_id=bank.id,
        request_id=request_id,
    )
    return {
        "success": True,
        "data": data,
    }


@router.post(
    "/me/demand/{request_id}/respond",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Respond to Emergency Demand with Real Stock Reservation",
)
async def respond_to_emergency_demand(
    request_id: uuid.UUID,
    data: BloodBankEmergencyRespondRequestSchema,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Accept or decline an emergency request with pessimistic row-level stock reservation."""
    bb_service = BloodBankService(db)
    bank = await bb_service.get_my_blood_bank(current_user.id)
    inv_service = InventoryService(db)
    result = await inv_service.respond_to_emergency_demand(
        blood_bank_id=bank.id,
        request_id=request_id,
        data=data,
        user_id=current_user.id,
    )
    return {
        "success": True,
        "message": f"Emergency response recorded with status '{result['status']}'",
        "data": result,
    }


@router.get(
    "",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="List Blood Banks Directory",
)
async def list_blood_banks(
    city: Optional[str] = Query(None, description="Filter by city"),
    is_24_hours: Optional[bool] = Query(None, description="Filter by 24/7 service"),
    is_verified: Optional[bool] = Query(None, description="Filter by verification"),
    pagination: dict[str, int] = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Public authenticated directory of blood banks."""
    service = BloodBankService(db)
    items, total = await service.list_blood_banks(
        city=city,
        is_24_hours=is_24_hours,
        is_verified=is_verified,
        limit=pagination["limit"],
        offset=pagination["offset"],
    )
    return {
        "success": True,
        "data": {
            "items": [BloodBankResponseSchema.model_validate(b).model_dump() for b in items],
            "total": total,
            "limit": pagination["limit"],
            "offset": pagination["offset"],
        },
    }


@router.get(
    "/{blood_bank_id}",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get Blood Bank Details by ID",
)
async def get_blood_bank_by_id(
    blood_bank_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get public facility profile of a specific blood bank."""
    service = BloodBankService(db)
    bank = await service.get_blood_bank_by_id(blood_bank_id)
    return {
        "success": True,
        "data": BloodBankResponseSchema.model_validate(bank).model_dump(),
    }

@router.delete(
    "/me",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Soft-delete blood bank account",
)
async def delete_my_blood_bank_account(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = BloodBankService(db)
    await service.delete_account(current_user.id)
    return {"success": True, "message": "Blood bank account deleted."}
