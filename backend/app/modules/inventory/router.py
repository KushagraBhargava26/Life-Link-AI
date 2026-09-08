# backend/app/modules/inventory/router.py
# LifeLink AI — Blood Inventory Module API Router
# Architecture Reference: ARCHITECTURE.md Section 24, ADR-001; API.md Section 10

from __future__ import annotations

import uuid
from typing import Any, Optional

import structlog
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError
from app.database import get_db
from app.dependencies import get_current_active_user
from app.modules.auth.models import User
from app.modules.blood_bank.repository import BloodBankRepository
from app.modules.inventory.models import FacilityTypeEnum
from app.modules.inventory.schemas import (
    BloodInventoryBatchUpdateSchema,
    BloodInventoryResponseSchema,
    BloodInventoryUpdateSchema,
    DemandAvailabilityResponseSchema,
    FacilityInventoryDashboardSchema,
)
from app.modules.inventory.service import InventoryService

logger = structlog.get_logger(__name__)

# Blood Bank scoped router (will be mounted or included in main)
blood_bank_inventory_router = APIRouter()
inventory_router = APIRouter()


async def _get_my_blood_bank_id(user: User, db: AsyncSession) -> uuid.UUID:
    """Helper to verify caller manages a registered blood bank."""
    repo = BloodBankRepository(db)
    bank = await repo.get_by_user_id(user.id)
    if not bank:
        raise NotFoundError("No blood bank facility profile associated with your account")
    return bank.id


@blood_bank_inventory_router.get(
    "/me/inventory",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get Own Blood Bank Inventory",
)
async def get_my_blood_bank_inventory(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Retrieve full cold-storage inventory breakdown and summary for the authenticated blood bank."""
    bank_id = await _get_my_blood_bank_id(current_user, db)
    service = InventoryService(db)
    data = await service.get_facility_inventory(FacilityTypeEnum.BLOOD_BANK.value, bank_id)
    return {
        "success": True,
        "data": {
            "items": [BloodInventoryResponseSchema.model_validate(i).model_dump() for i in data["items"]],
            "summary": data["summary"],
        },
    }


@blood_bank_inventory_router.put(
    "/me/inventory/{blood_type}",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Update Blood Type Stock",
)
async def update_my_blood_bank_stock(
    blood_type: str,
    data: BloodInventoryUpdateSchema,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Update available stock, buffer threshold, and expiry date for a blood type."""
    bank_id = await _get_my_blood_bank_id(current_user, db)
    service = InventoryService(db)
    updated = await service.update_stock(
        facility_type=FacilityTypeEnum.BLOOD_BANK.value,
        facility_id=bank_id,
        blood_type=blood_type,
        data=data,
        user_id=current_user.id,
    )
    return {
        "success": True,
        "message": f"Inventory for {blood_type} updated successfully",
        "data": BloodInventoryResponseSchema.model_validate(updated).model_dump(),
    }


@blood_bank_inventory_router.put(
    "/me/inventory",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Batch Update Blood Inventory",
)
async def batch_update_my_blood_bank_stock(
    data: BloodInventoryBatchUpdateSchema,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Batch update multiple blood types simultaneously."""
    bank_id = await _get_my_blood_bank_id(current_user, db)
    service = InventoryService(db)
    updated_items = await service.batch_update_stock(
        facility_type=FacilityTypeEnum.BLOOD_BANK.value,
        facility_id=bank_id,
        data=data,
        user_id=current_user.id,
    )
    return {
        "success": True,
        "message": f"Batch update successful for {len(updated_items)} blood types",
        "data": [BloodInventoryResponseSchema.model_validate(i).model_dump() for i in updated_items],
    }


@blood_bank_inventory_router.get(
    "/me/demand/{request_id}/availability",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Check Compatible Stock Availability for Requisition",
)
async def check_demand_availability(
    request_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Check whether this blood bank has compatible available inventory for an emergency requisition.
    Deterministic compatibility logic applied; zero patient PII exposed.
    """
    bank_id = await _get_my_blood_bank_id(current_user, db)
    service = InventoryService(db)
    availability = await service.check_demand_availability(
        facility_type=FacilityTypeEnum.BLOOD_BANK.value,
        facility_id=bank_id,
        request_id=request_id,
    )
    return {
        "success": True,
        "data": DemandAvailabilityResponseSchema.model_validate(availability).model_dump(),
    }


@blood_bank_inventory_router.get(
    "/{blood_bank_id}/inventory",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Public Blood Bank Inventory Directory",
)
async def get_public_blood_bank_inventory(
    blood_bank_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Public read-only inventory lookup for verified blood bank facilities."""
    service = InventoryService(db)
    data = await service.get_facility_inventory(FacilityTypeEnum.BLOOD_BANK.value, blood_bank_id)
    return {
        "success": True,
        "data": {
            "items": [BloodInventoryResponseSchema.model_validate(i).model_dump() for i in data["items"]],
            "summary": data["summary"],
        },
    }
