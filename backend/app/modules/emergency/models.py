# backend/app/modules/emergency/models.py
# LifeLink AI — Emergency Module SQLAlchemy ORM Models
# Architecture Reference: ARCHITECTURE.md Section 24 (Database Overview)
# Full schema defined in DATABASE.md
#
# Rules:
# - All models inherit from app.database.Base
# - Every table has: id (UUID), created_at, updated_at, deleted_at (soft delete)
# - No raw SQL — always use SQLAlchemy ORM
#
# Phase 1.1: Empty models — no tables defined yet.
# Phase 1.2+: Define SQLAlchemy ORM models here based on DATABASE.md.

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.modules.hospital.models import Hospital

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class BloodTypeEnum(str, enum.Enum):
    O_NEG = "O-"
    O_POS = "O+"
    A_NEG = "A-"
    A_POS = "A+"
    B_NEG = "B-"
    B_POS = "B+"
    AB_NEG = "AB-"
    AB_POS = "AB+"


class UrgencyLevelEnum(str, enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class EmergencyStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    MATCHING = "MATCHING"
    NOTIFIED = "NOTIFIED"
    CONFIRMED = "CONFIRMED"
    IN_PROGRESS = "IN_PROGRESS"
    PARTIALLY_FULFILLED = "PARTIALLY_FULFILLED"
    FULFILLED = "FULFILLED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class EmergencyRequest(Base):
    __tablename__ = "emergency_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    request_number: Mapped[str] = mapped_column(
        String(20), unique=True, index=True, nullable=False
    )
    requested_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )
    patient_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    patient_age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    blood_type: Mapped[str] = mapped_column(
        String(10), index=True, nullable=False
    )
    units_required: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    units_fulfilled: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    urgency_level: Mapped[str] = mapped_column(
        String(20), index=True, nullable=False, default=UrgencyLevelEnum.CRITICAL.value
    )
    hospital_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    hospital_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hospitals.id", ondelete="SET NULL"), index=True, nullable=True
    )
    facility_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[str] = mapped_column(String(100), index=True, nullable=False, default="Mumbai")
    latitude: Mapped[Optional[float]] = mapped_column(Numeric(10, 8), nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Numeric(11, 8), nullable=True)

    # Relationship
    hospital: Mapped[Optional["Hospital"]] = relationship("Hospital", back_populates="emergency_requests")
    status: Mapped[str] = mapped_column(
        String(30), index=True, nullable=False, default=EmergencyStatusEnum.PENDING.value
    )
    ai_assisted: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    fulfilled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancellation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
