# backend/app/modules/hospital/schemas.py
# LifeLink AI — Hospital Module Pydantic Schemas
# Architecture Reference: ARCHITECTURE.md Section 27; API.md Section 8

from __future__ import annotations

import re
import uuid
from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.hospital.models import HospitalTypeEnum


class HospitalCreateSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, description="Official hospital name")
    registration_number: Optional[str] = Field(None, max_length=100, description="Government registry number")
    type: HospitalTypeEnum = Field(default=HospitalTypeEnum.PRIVATE)
    address_line: str = Field(..., min_length=5, max_length=255)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    pincode: str = Field(..., min_length=4, max_length=10)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    phone: str = Field(..., min_length=7, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=255)
    bed_count: Optional[int] = Field(None, ge=1)
    has_blood_bank: bool = Field(default=False)
    license_issue_date: Optional[date] = Field(None, description="Statutory license issue date")
    license_expiry_date: Optional[date] = Field(None, description="Statutory license expiry date")
    certificate_url: Optional[str] = Field(None, max_length=512, description="Certificate document URL or storage path")
    status: str = Field(default="ACTIVE", description="Operational status: ACTIVE, SUSPENDED, BLOCKED")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Hospital name cannot be empty.")
        return clean

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        clean = v.strip()
        digits = re.sub(r"\D", "", clean)
        if len(digits) < 7 or len(digits) > 15:
            raise ValueError("Phone number must contain between 7 and 15 digits.")
        return clean

    @field_validator("pincode")
    @classmethod
    def validate_pincode(cls, v: str) -> str:
        clean = v.strip()
        if not clean.isdigit() or len(clean) < 4 or len(clean) > 10:
            raise ValueError("Pincode must be numeric and between 4 and 10 digits.")
        return clean


class HospitalUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    registration_number: Optional[str] = Field(None, max_length=100)
    type: Optional[HospitalTypeEnum] = None
    address_line: Optional[str] = Field(None, min_length=5, max_length=255)
    city: Optional[str] = Field(None, min_length=2, max_length=100)
    state: Optional[str] = Field(None, min_length=2, max_length=100)
    pincode: Optional[str] = Field(None, min_length=4, max_length=10)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    phone: Optional[str] = Field(None, min_length=7, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=255)
    bed_count: Optional[int] = Field(None, ge=1)
    has_blood_bank: Optional[bool] = None
    license_issue_date: Optional[date] = None
    license_expiry_date: Optional[date] = None
    certificate_url: Optional[str] = None
    status: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        clean = v.strip()
        if not clean:
            return None
        digits = re.sub(r"\D", "", clean)
        if len(digits) < 7 or len(digits) > 15:
            raise ValueError("Phone number must contain between 7 and 15 digits.")
        return clean

    @field_validator("pincode")
    @classmethod
    def validate_pincode(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        clean = v.strip()
        if not clean:
            return None
        if not clean.isdigit() or len(clean) < 4 or len(clean) > 10:
            raise ValueError("Pincode must be numeric and between 4 and 10 digits.")
        return clean


class HospitalResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    registration_number: Optional[str] = None
    type: HospitalTypeEnum
    address_line: str
    city: str
    state: str
    pincode: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: str
    email: Optional[str] = None
    website: Optional[str] = None
    bed_count: Optional[int] = None
    has_blood_bank: bool
    license_issue_date: Optional[date] = None
    license_expiry_date: Optional[date] = None
    certificate_url: Optional[str] = None
    status: str = "ACTIVE"
    is_verified: bool
    is_active: bool
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime


class HospitalStaffResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    hospital_id: uuid.UUID
    user_id: uuid.UUID
    designation: Optional[str] = None
    is_primary: bool
    can_manage_inventory: bool
    can_create_requests: bool
    created_at: datetime


class HospitalDashboardSchema(BaseModel):
    hospital: HospitalResponseSchema
    active_requests_count: int
    pending_requests_count: int
    recent_requests: list[dict[str, Any]] = Field(default_factory=list)
