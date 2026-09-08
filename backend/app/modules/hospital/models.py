# backend/app/modules/hospital/models.py
# LifeLink AI — Hospital Module SQLAlchemy ORM Models
# Architecture Reference: ARCHITECTURE.md Section 24; DATABASE.md Section 7

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.modules.auth.models import User
    from app.modules.emergency.models import EmergencyRequest


class HospitalTypeEnum(str, enum.Enum):
    GOVERNMENT = "GOVERNMENT"
    PRIVATE = "PRIVATE"
    TRUST = "TRUST"
    CLINIC = "CLINIC"
    SPECIALTY = "SPECIALTY"


class Hospital(Base):
    __tablename__ = "hospitals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    registration_number: Mapped[Optional[str]] = mapped_column(
        String(100), unique=True, nullable=True
    )
    type: Mapped[HospitalTypeEnum] = mapped_column(
        SAEnum(HospitalTypeEnum, name="hospital_type_enum"),
        default=HospitalTypeEnum.PRIVATE,
        nullable=False,
    )
    address_line: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    pincode: Mapped[str] = mapped_column(String(10), nullable=False)
    latitude: Mapped[Optional[float]] = mapped_column(Numeric(10, 8), nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Numeric(11, 8), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    bed_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    has_blood_bank: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    license_issue_date: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)
    license_expiry_date: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)
    certificate_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False, index=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    # Relationships
    staff: Mapped[list["HospitalStaff"]] = relationship(
        "HospitalStaff", back_populates="hospital", cascade="all, delete-orphan"
    )
    emergency_requests: Mapped[list["EmergencyRequest"]] = relationship(
        "EmergencyRequest", back_populates="hospital"
    )


class HospitalStaff(Base):
    __tablename__ = "hospital_staff"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    hospital_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("hospitals.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    designation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_manage_inventory: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_create_requests: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    joined_at: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    hospital: Mapped["Hospital"] = relationship("Hospital", back_populates="staff")
    user: Mapped["User"] = relationship("User")

    __table_args__ = (
        UniqueConstraint("hospital_id", "user_id", name="uq_hospital_staff_hospital_user"),
    )
