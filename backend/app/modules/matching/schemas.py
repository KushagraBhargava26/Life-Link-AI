"""Matching module Pydantic schemas."""

from __future__ import annotations
import uuid
from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field


class MatchCandidateResponseSchema(BaseModel):
    """Clean, explainable candidate recommendation representation."""

    id: uuid.UUID
    rank: int
    candidate_type: str = Field(description="DONOR or BLOOD_BANK")
    candidate_id: str = Field(description="UUID of donor or blood bank")
    name: str = Field(description="Display label e.g. 'Donor #A49F' or facility name")
    blood_type: str = Field(description="ABO/Rh group e.g. O-, A+")
    compatibility_score: float
    proximity_score: float
    availability_score: float
    ai_score: Optional[float] = None
    total_score: float
    distance_km: Optional[float] = None
    units_available: Optional[int] = None
    status: str = "PROPOSED"
    donor_response_status: Optional[str] = Field(
        default=None,
        description="ACCEPTED, DECLINED, or PENDING response from donor",
    )
    blood_bank_response_status: Optional[str] = Field(
        default=None,
        description="ACCEPTED, PARTIALLY_ACCEPTED, or DECLINED response from blood bank",
    )
    units_committed: Optional[int] = Field(
        default=None,
        description="Units committed by blood bank",
    )
    explanation: List[str] = Field(default_factory=list)
    location_display: str = Field(description="Human readable proximity e.g. '4.2 km away'")
    is_compatible: bool = True

    model_config = {"from_attributes": True}


class MatchRunResponseSchema(BaseModel):
    """Complete match run result containing ranked blood banks and donors."""

    id: uuid.UUID
    emergency_request_id: uuid.UUID
    run_number: int
    status: str
    model_version: str
    algorithm: str
    search_radius_km: float
    candidates_evaluated: int
    donors_matched: int
    blood_banks_matched: int
    execution_duration_ms: Optional[float] = None
    created_at: datetime
    blood_banks: List[MatchCandidateResponseSchema] = Field(default_factory=list)
    donors: List[MatchCandidateResponseSchema] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class CandidateStatusUpdateSchema(BaseModel):
    """Schema for updating a candidate's operational status."""

    status: str = Field(description="PROPOSED, SHORTLISTED, or DISMISSED")
