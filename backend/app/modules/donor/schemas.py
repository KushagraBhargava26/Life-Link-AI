# backend/app/modules/donor/schemas.py
# LifeLink AI — Donor Module Pydantic v2 Schemas
# Architecture Reference: ARCHITECTURE.md Section 33 & API.md Section 7

from __future__ import annotations

import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


VALID_BLOOD_TYPES = {"O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"}
VALID_GENDERS = {"MALE", "FEMALE", "OTHER", "PREFER_NOT_TO_SAY"}


class DonorCreateSchema(BaseModel):
    blood_type: str = Field(..., description="ABO/Rh Blood Type (e.g. O-, A+)")
    city: str = Field(..., min_length=2, max_length=100, description="City of residence")
    state: Optional[str] = Field(default=None, max_length=100)
    pincode: Optional[str] = Field(default=None, max_length=10)
    weight_kg: Optional[float] = Field(default=None, ge=45.0, le=250.0, description="Weight in kg (minimum 45kg for eligibility)")
    date_of_birth: Optional[datetime.date] = None
    gender: Optional[str] = None
    address_line: Optional[str] = Field(default=None, max_length=255)
    is_available: bool = Field(default=True, description="Available to receive emergency blood requests")

    @field_validator("blood_type")
    @classmethod
    def validate_blood_type(cls, v: str) -> str:
        clean = v.strip().upper()
        if clean not in VALID_BLOOD_TYPES:
            raise ValueError(f"Invalid blood type '{v}'. Must be one of: {', '.join(sorted(VALID_BLOOD_TYPES))}")
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

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        clean = v.strip().upper()
        if clean not in VALID_GENDERS:
            raise ValueError(f"Invalid gender '{v}'. Must be one of: {', '.join(sorted(VALID_GENDERS))}")
        return clean


class DonorUpdateSchema(BaseModel):
    blood_type: Optional[str] = None
    city: Optional[str] = Field(default=None, min_length=2, max_length=100)
    state: Optional[str] = None
    pincode: Optional[str] = None
    weight_kg: Optional[float] = Field(default=None, ge=45.0, le=250.0)
    date_of_birth: Optional[datetime.date] = None
    gender: Optional[str] = None
    address_line: Optional[str] = None
    is_available: Optional[bool] = None
    last_donation_date: Optional[datetime.date] = None

    @field_validator("blood_type")
    @classmethod
    def validate_blood_type(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        clean = v.strip().upper()
        if clean not in VALID_BLOOD_TYPES:
            raise ValueError(f"Invalid blood type '{v}'. Must be one of: {', '.join(sorted(VALID_BLOOD_TYPES))}")
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


class DonorAvailabilityToggleSchema(BaseModel):
    is_available: bool = Field(..., description="Donor-controlled emergency availability toggle")


class DonorResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    blood_type: str
    city: str
    state: Optional[str] = None
    pincode: Optional[str] = None
    weight_kg: Optional[float] = None
    date_of_birth: Optional[datetime.date] = None
    gender: Optional[str] = None
    address_line: Optional[str] = None
    is_available: bool
    is_eligible: bool
    last_donation_date: Optional[datetime.date] = None
    total_donations: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


class CompatibleEmergencyOpportunitySchema(BaseModel):
    id: uuid.UUID
    request_number: str
    blood_type: str
    component: str
    units_requested: int
    urgency_level: str
    hospital_name: Optional[str] = None
    city: str
    state: str
    created_at: datetime.datetime


class DonorDashboardSchema(BaseModel):
    profile: Optional[DonorResponseSchema] = None
    has_profile: bool
    is_available: bool
    is_eligible: bool
    next_eligible_date: Optional[datetime.date] = None
    days_until_eligible: int
    total_donations: int
    estimated_lives_saved: int
    compatible_opportunities: list[CompatibleEmergencyOpportunitySchema]


class DonorOpportunityResponseCreateSchema(BaseModel):
    status: str = Field(default="ACCEPTED", description="ACCEPTED or DECLINED")
    notes: Optional[str] = Field(default=None, max_length=500, description="Optional note or estimated arrival")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        clean = v.strip().upper()
        if clean not in {"ACCEPTED", "DECLINED", "PENDING"}:
            raise ValueError("Status must be ACCEPTED, DECLINED, or PENDING.")
        return clean


class DonorOpportunityResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    emergency_request_id: uuid.UUID
    donor_id: uuid.UUID
    status: str
    notes: Optional[str] = None
    responded_at: datetime.datetime
    created_at: datetime.datetime


class DonorOpportunityDetailSchema(BaseModel):
    id: uuid.UUID
    request_number: str
    blood_type: str
    component: str
    units_requested: int
    units_fulfilled: int
    urgency_level: str
    hospital_name: Optional[str] = None
    facility_address: Optional[str] = None
    city: str
    status: str
    created_at: datetime.datetime
    is_compatible: bool
    donor_blood_type: str
    donor_response: Optional[DonorOpportunityResponseSchema] = None


