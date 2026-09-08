# backend/app/modules/emergency/schemas.py
# LifeLink AI — Emergency Module Pydantic Schemas
# Architecture Reference: ARCHITECTURE.md Section 16 (Backend Architecture)
# Full request/response contracts defined in API.md
#
# Rules:
# - All schemas use Pydantic v2
# - Request schemas named: {Resource}CreateSchema, {Resource}UpdateSchema
# - Response schemas named: {Resource}ResponseSchema
# - All schemas must have type hints on every field
#
# Phase 1.1: Empty schemas — no request/response models defined yet.
# Phase 1.2+: Define Pydantic v2 schemas based on API.md.

from __future__ import annotations

import re
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


VALID_BLOOD_TYPES = {"O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"}
VALID_URGENCY_LEVELS = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}


class EmergencyRequestCreateSchema(BaseModel):
    blood_type: str = Field(..., description="ABO and Rh blood type (e.g. O-, A+)")
    units_required: int = Field(default=1, ge=1, le=20, description="Units required (1-20)")
    urgency_level: str = Field(default="CRITICAL", description="Urgency priority")
    hospital_name: Optional[str] = Field(default=None, max_length=200, description="Destination hospital name")
    hospital_id: Optional[uuid.UUID] = Field(default=None, description="Registered hospital UUID")
    facility_address: Optional[str] = Field(default=None, description="Facility address")
    city: str = Field(default="Mumbai", min_length=2, max_length=100, description="City of emergency")
    patient_name: Optional[str] = Field(default=None, max_length=200, description="Patient name")
    patient_age: Optional[int] = Field(default=None, ge=1, le=120, description="Patient age")
    latitude: Optional[float] = Field(default=None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(default=None, ge=-180.0, le=180.0)
    notes: Optional[str] = Field(default=None, max_length=1000, description="Clinical notes")

    @field_validator("blood_type")
    @classmethod
    def validate_blood_type(cls, v: str) -> str:
        clean = v.strip().upper()
        if clean not in VALID_BLOOD_TYPES:
            raise ValueError(f"Invalid blood type '{v}'. Must be one of: {', '.join(sorted(VALID_BLOOD_TYPES))}")
        return clean

    @field_validator("patient_name")
    @classmethod
    def validate_patient_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        clean = v.strip()
        if not clean:
            return None
        if re.search(r"\d", clean):
            raise ValueError("Patient name cannot contain numbers.")
        if not re.match(r"^[a-zA-Z\s\-\'\.]+$", clean):
            raise ValueError("Patient name contains invalid characters.")
        return clean

    @field_validator("urgency_level")
    @classmethod
    def validate_urgency(cls, v: str) -> str:
        clean = v.strip().upper()
        if clean not in VALID_URGENCY_LEVELS:
            raise ValueError(f"Invalid urgency level '{v}'. Must be one of: {', '.join(sorted(VALID_URGENCY_LEVELS))}")
        return clean


class EmergencyPublicTrackingSchema(BaseModel):
    """
    Zero-PII schema for public tracking.
    Never exposes patient_name, patient_age, or clinical notes.
    """
    model_config = ConfigDict(from_attributes=True)

    id: Optional[uuid.UUID] = None
    request_number: str
    blood_type: str
    units_required: int
    units_fulfilled: int
    urgency_level: str
    hospital_name: Optional[str] = None
    city: str
    status: str
    created_at: datetime
    updated_at: datetime


class EmergencyRequestResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    request_number: str
    blood_type: str
    units_required: int
    units_fulfilled: int
    urgency_level: str
    hospital_name: Optional[str] = None
    facility_address: Optional[str] = None
    city: str
    status: str
    ai_assisted: bool
    patient_name: Optional[str] = None
    patient_age: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class EmergencyStatusResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    request_number: str
    status: str
    units_required: int
    units_fulfilled: int
    updated_at: datetime


class EmergencyStatusUpdateSchema(BaseModel):
    status: str = Field(..., description="PENDING, MATCHING, IN_PROGRESS, FULFILLED, CANCELLED")
    cancellation_reason: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)
