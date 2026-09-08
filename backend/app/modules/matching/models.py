"""Matching module SQLAlchemy ORM models."""

from __future__ import annotations
import enum
import uuid
from datetime import datetime
from typing import Optional, List, Any

from sqlalchemy import (
    String,
    Integer,
    Float,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class MatchRunStatusEnum(str, enum.Enum):
    INITIATED = "INITIATED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    NO_CANDIDATES = "NO_CANDIDATES"


class MatchCandidateTypeEnum(str, enum.Enum):
    DONOR = "DONOR"
    BLOOD_BANK = "BLOOD_BANK"


class MatchCandidateStatusEnum(str, enum.Enum):
    PROPOSED = "PROPOSED"
    SHORTLISTED = "SHORTLISTED"
    DISMISSED = "DISMISSED"


match_run_status_db_enum = ENUM(
    MatchRunStatusEnum,
    name="match_run_status_enum",
    create_type=False,
)

match_candidate_type_db_enum = ENUM(
    MatchCandidateTypeEnum,
    name="match_candidate_type_enum",
    create_type=False,
)

match_candidate_status_db_enum = ENUM(
    MatchCandidateStatusEnum,
    name="match_candidate_status_enum",
    create_type=False,
)


class MatchRun(Base):
    """Auditable record of an emergency matching execution."""

    __tablename__ = "match_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    emergency_request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("emergency_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    run_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )
    status: Mapped[MatchRunStatusEnum] = mapped_column(
        match_run_status_db_enum,
        nullable=False,
        default=MatchRunStatusEnum.INITIATED,
        index=True,
    )
    model_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="donor-response-v1",
    )
    algorithm: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="deterministic_ai_hybrid",
    )
    search_radius_km: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=50.0,
    )
    candidates_evaluated: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    donors_matched: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    blood_banks_matched: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    execution_duration_ms: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    executed_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        onupdate=datetime.utcnow,
        nullable=False,
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    candidates: Mapped[List[MatchCandidate]] = relationship(
        "MatchCandidate",
        back_populates="match_run",
        cascade="all, delete-orphan",
        order_by="MatchCandidate.rank",
    )

    __table_args__ = (
        UniqueConstraint("emergency_request_id", "run_number", name="uq_match_runs_request_run_number"),
    )


class MatchCandidate(Base):
    """Ranked candidate (donor or blood bank) from a matching run."""

    __tablename__ = "match_candidates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    match_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("match_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    emergency_request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("emergency_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    candidate_type: Mapped[MatchCandidateTypeEnum] = mapped_column(
        match_candidate_type_db_enum,
        nullable=False,
    )
    donor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("donors.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    blood_bank_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("blood_banks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    rank: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    total_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    compatibility_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    proximity_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    availability_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    ai_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    distance_km: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    units_available: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )
    status: Mapped[MatchCandidateStatusEnum] = mapped_column(
        match_candidate_status_db_enum,
        nullable=False,
        default=MatchCandidateStatusEnum.PROPOSED,
        index=True,
    )
    explanation: Mapped[Optional[Any]] = mapped_column(
        JSONB,
        nullable=True,
    )
    candidate_metadata: Mapped[Optional[Any]] = mapped_column(
        JSONB,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        onupdate=datetime.utcnow,
        nullable=False,
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    match_run: Mapped[MatchRun] = relationship(
        "MatchRun",
        back_populates="candidates",
    )

    __table_args__ = (
        UniqueConstraint("match_run_id", "rank", name="uq_match_candidates_run_rank"),
    )
