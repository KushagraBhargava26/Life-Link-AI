# backend/app/modules/inventory/schemas.py
# LifeLink AI — Blood Inventory Module Pydantic Schemas
# Architecture Reference: ARCHITECTURE.md Section 24; API.md Section 10

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.medical import VALID_BLOOD_TYPES, VALID_COMPONENTS
from app.modules.inventory.models import FacilityTypeEnum, InventoryChangeEnum


class BloodInventoryUpdateSchema(BaseModel):
    units_available: int = Field(..., ge=0, description="Physical units available in cold storage")
    minimum_threshold: int = Field(default=5, ge=0, description="Minimum safe buffer threshold")
    expiry_date: Optional[date] = Field(None, description="Earliest expiry date of current held stock")
    component: str = Field(default="WHOLE_BLOOD", description="Blood component category")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for stock modification")

    @field_validator("component")
    @classmethod
    def validate_component(cls, v: str) -> str:
        upper_v = v.strip().upper()
        if upper_v not in VALID_COMPONENTS:
            raise ValueError(f"Invalid component '{v}'. Allowed: {sorted(VALID_COMPONENTS)}")
        return upper_v


class BloodInventoryBatchItem(BaseModel):
    blood_type: str = Field(..., description="e.g. O+, A-")
    component: str = Field(default="WHOLE_BLOOD")
    units_available: int = Field(..., ge=0)
    minimum_threshold: int = Field(default=5, ge=0)
    expiry_date: Optional[date] = None
    reason: Optional[str] = None

    @field_validator("blood_type")
    @classmethod
    def validate_blood_type(cls, v: str) -> str:
        upper_v = v.strip().upper()
        if upper_v not in VALID_BLOOD_TYPES:
            raise ValueError(f"Invalid blood type '{v}'. Allowed: {sorted(VALID_BLOOD_TYPES)}")
        return upper_v

    @field_validator("component")
    @classmethod
    def validate_component(cls, v: str) -> str:
        upper_v = v.strip().upper()
        if upper_v not in VALID_COMPONENTS:
            raise ValueError(f"Invalid component '{v}'. Allowed: {sorted(VALID_COMPONENTS)}")
        return upper_v


class BloodInventoryBatchUpdateSchema(BaseModel):
    items: list[BloodInventoryBatchItem] = Field(..., min_length=1)


class BloodInventoryResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    facility_type: FacilityTypeEnum
    facility_id: uuid.UUID
    blood_type: str
    component: str
    units_available: int
    units_reserved: int
    net_available: int
    minimum_threshold: int
    last_restocked_at: Optional[datetime] = None
    expiry_date: Optional[date] = None
    is_expired: bool
    is_low_stock: bool
    created_at: datetime
    updated_at: datetime


class InventorySummarySchema(BaseModel):
    total_available: int
    total_reserved: int
    expiring_soon_count: int
    depleted_groups_count: int
    stock_by_blood_type: dict[str, int]


class FacilityInventoryDashboardSchema(BaseModel):
    items: list[BloodInventoryResponseSchema]
    summary: InventorySummarySchema


class CompatibleStockBreakdownItem(BaseModel):
    blood_type: str
    units_available: int
    is_exact_match: bool


class DemandAvailabilityResponseSchema(BaseModel):
    request_id: uuid.UUID
    request_number: str
    blood_type: str
    component: str
    units_required: int
    urgency_level: str
    hospital_name: str
    city: str
    status: str
    is_compatible_stock_available: bool
    availability_status: str  # 'AVAILABLE', 'PARTIAL', 'UNAVAILABLE'
    total_compatible_units: int
    compatible_breakdown: list[CompatibleStockBreakdownItem]


class BloodBankEmergencyRespondRequestSchema(BaseModel):
    units_committed: int = Field(..., ge=0, description="Units of blood committed from available inventory")
    blood_type: Optional[str] = Field(None, description="Specific blood group committed, defaults to request blood type")
    status: str = Field(default="ACCEPTED", description="ACCEPTED, PARTIALLY_ACCEPTED, or DECLINED")
    message: Optional[str] = Field(None, max_length=500, description="Coordination or delivery notes")


class BloodBankEmergencyResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    emergency_request_id: uuid.UUID
    blood_bank_id: uuid.UUID
    blood_bank_name: Optional[str] = None
    blood_type: str
    units_requested: int
    units_committed: int
    status: str
    message: Optional[str] = None
    responded_by: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
