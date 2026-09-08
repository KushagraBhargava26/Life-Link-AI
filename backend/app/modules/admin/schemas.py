# backend/app/modules/admin/schemas.py
# LifeLink AI — Admin Module Pydantic v2 Schemas
# Architecture Reference: ARCHITECTURE.md Section 22

from __future__ import annotations

import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class VerificationUpdateSchema(BaseModel):
    is_verified: bool = Field(default=True, description="Verification status flag")


class FacilityStatusUpdateSchema(BaseModel):
    status: str = Field(..., description="ACTIVE, SUSPENDED, BLOCKED")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for suspension or block")


class PendingHospitalSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    registration_number: Optional[str] = None
    type: str
    city: str
    state: str
    phone: str
    email: Optional[str] = None
    license_issue_date: Optional[datetime.date] = None
    license_expiry_date: Optional[datetime.date] = None
    certificate_url: Optional[str] = None
    status: str = "ACTIVE"
    is_verified: bool
    created_at: datetime.datetime


class PendingBloodBankSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    license_number: Optional[str] = None
    city: str
    state: str
    phone: str
    email: Optional[str] = None
    is_24_hours: bool
    license_issue_date: Optional[datetime.date] = None
    license_expiry_date: Optional[datetime.date] = None
    certificate_url: Optional[str] = None
    status: str = "ACTIVE"
    is_verified: bool
    created_at: datetime.datetime


class PendingVerificationsResponseSchema(BaseModel):
    hospitals: list[PendingHospitalSchema]
    blood_banks: list[PendingBloodBankSchema]
    total_pending: int


class AdminFacilityListResponseSchema(BaseModel):
    hospitals: list[PendingHospitalSchema]
    blood_banks: list[PendingBloodBankSchema]
    total_active: int
    total_suspended: int
    total_blocked: int

