# backend/app/modules/blood_bank/schemas.py
# LifeLink AI — Blood Bank Module Pydantic Schemas
# Architecture Reference: ARCHITECTURE.md Section 27; API.md Section 9

from __future__ import annotations

import re
import uuid
from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BloodBankCreateSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, description="Official blood bank name")
    license_number: Optional[str] = Field(None, max_length=100, description="State blood bank license number")
    hospital_id: Optional[uuid.UUID] = Field(None, description="Attached hospital UUID if in-house")
    address_line: str = Field(..., min_length=5, max_length=255)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    pincode: str = Field(..., min_length=4, max_length=10)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    phone: str = Field(..., min_length=7, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    operating_hours: Optional[str] = Field(None, max_length=255, description="e.g. 24/7 or 09:00 - 18:00")
    is_24_hours: bool = Field(default=False)
    accepts_walk_in: bool = Field(default=True)
    license_issue_date: Optional[date] = Field(None, description="Statutory license issue date")
    license_expiry_date: Optional[date] = Field(None, description="Statutory license expiry date")
    certificate_url: Optional[str] = Field(None, max_length=512, description="Certificate document URL or storage path")
    status: str = Field(default="ACTIVE", description="Operational status: ACTIVE, SUSPENDED, BLOCKED")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Blood bank name cannot be empty.")
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


class BloodBankUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    license_number: Optional[str] = Field(None, max_length=100)
    hospital_id: Optional[uuid.UUID] = None
    address_line: Optional[str] = Field(None, min_length=5, max_length=255)
    city: Optional[str] = Field(None, min_length=2, max_length=100)
    state: Optional[str] = Field(None, min_length=2, max_length=100)
    pincode: Optional[str] = Field(None, min_length=4, max_length=10)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    phone: Optional[str] = Field(None, min_length=7, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    operating_hours: Optional[str] = Field(None, max_length=255)
    is_24_hours: Optional[bool] = None
    accepts_walk_in: Optional[bool] = None
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


class BloodBankResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    license_number: Optional[str] = None
    hospital_id: Optional[uuid.UUID] = None
    address_line: str
    city: str
    state: str
    pincode: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: str
    email: Optional[str] = None
    operating_hours: Optional[str] = None
    is_24_hours: bool
    accepts_walk_in: bool
    license_issue_date: Optional[date] = None
    license_expiry_date: Optional[date] = None
    certificate_url: Optional[str] = None
    status: str = "ACTIVE"
    is_verified: bool
    is_active: bool
    manager_user_id: Optional[uuid.UUID] = None
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime


class BloodBankDashboardSchema(BaseModel):
    blood_bank: BloodBankResponseSchema
    active_emergency_demand_count: int
    is_operational: bool
    emergency_demand: list[dict[str, Any]] = Field(default_factory=list)
