# ai/app/modules/matching/schemas.py
# LifeLink AI — Matching Engine Pydantic Schemas
# Architecture Reference: ARCHITECTURE.md Section 17 & 20

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


class DonorCandidateFeatureVector(BaseModel):
    """Features of a pre-filtered compatible donor candidate."""

    donor_id: str = Field(description="Unique donor UUID")
    blood_type: str = Field(description="Donor blood group e.g. O-, A+")
    compatibility_score: float = Field(default=1.0, ge=0.0, le=1.0, description="1.0 for exact, 0.8 for universal")
    availability_score: float = Field(default=1.0, ge=0.0, le=1.0, description="1.0 for active & available")
    recency_months: float = Field(default=12.0, ge=0.0, description="Months since last donation")
    frequency_donations: int = Field(default=1, ge=0, description="Total past donations count")
    time_months: float = Field(default=24.0, ge=0.0, description="Months since first donation / registration")
    distance_km: Optional[float] = Field(default=None, ge=0.0, description="Haversine distance in km from emergency location")


class RankDonorsRequest(BaseModel):
    """Input payload for ranking compatible donor candidates."""

    request_id: str = Field(description="Emergency request UUID")
    blood_type_required: str = Field(description="Requested blood type")
    urgency_level: str = Field(default="CRITICAL", description="Urgency: CRITICAL, HIGH, MEDIUM, LOW")
    search_radius_km: float = Field(default=50.0, gt=0.0)
    candidates: List[DonorCandidateFeatureVector] = Field(default_factory=list)


class RankedDonorCandidate(BaseModel):
    """A ranked donor recommendation with explainable scoring."""

    donor_id: str
    rank: int
    total_score: float = Field(ge=0.0, le=1.0)
    compatibility_score: float = Field(ge=0.0, le=1.0)
    proximity_score: float = Field(ge=0.0, le=1.0)
    availability_score: float = Field(ge=0.0, le=1.0)
    propensity_score: float = Field(ge=0.0, le=1.0)
    distance_km: Optional[float] = None
    explanation: List[str] = Field(default_factory=list)


class RankDonorsResponse(BaseModel):
    """Output payload from donor ranking engine."""
    model_config = {"protected_namespaces": ()}

    request_id: str
    model_version: str = "donor-response-v1"
    algorithm: str = "calibrated_logistic_regression_hybrid"
    candidates_ranked: int
    candidates: List[RankedDonorCandidate] = Field(default_factory=list)
