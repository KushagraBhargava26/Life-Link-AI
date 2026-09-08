# backend/app/modules/donor/models.py
# LifeLink AI — Donor Module SQLAlchemy ORM Models
# Architecture Reference: ARCHITECTURE.md Section 33 & DATABASE.md Section 6

from __future__ import annotations

import datetime
import uuid
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Donor(Base):
    """
    Voluntary blood donor profile record.
    Linked 1-to-1 with a User record in the auth module.
    """
    __tablename__ = "donors"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    blood_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
    )
    date_of_birth: Mapped[Optional[datetime.date]] = mapped_column(
        Date,
        nullable=True,
    )
    gender: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
    )
    weight_kg: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    address_line: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )
    state: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    pincode: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
    )
    latitude: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 8),
        nullable=True,
    )
    longitude: Mapped[Optional[float]] = mapped_column(
        Numeric(11, 8),
        nullable=True,
    )
    is_available: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )
    is_eligible: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )
    last_donation_date: Mapped[Optional[datetime.date]] = mapped_column(
        Date,
        nullable=True,
    )
    total_donations: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    medical_conditions: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    fcm_token: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
    )
    notification_email: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    notification_push: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    # Relationship to user
    user = relationship("User", lazy="joined")


class DonorEmergencyResponse(Base):
    """
    Explicit voluntary donor response to an active emergency requisition.
    Guarded by ReBAC to ensure donors can only respond on their own behalf.
    """
    __tablename__ = "donor_emergency_responses"
    __table_args__ = (
        UniqueConstraint("emergency_request_id", "donor_id", name="uq_donor_emergency_responses_req_donor"),
    )

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
    donor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("donors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="ACCEPTED",
        index=True,
    )
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    responded_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    donor = relationship("Donor", lazy="joined")
    emergency_request = relationship("EmergencyRequest", lazy="joined")

