# backend/app/modules/inventory/models.py
# LifeLink AI — Blood Inventory Module SQLAlchemy ORM Models
# Architecture Reference: ARCHITECTURE.md Section 24, ADR-001; DATABASE.md Section 9

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.modules.auth.models import User
    from app.modules.blood_bank.models import BloodBank
    from app.modules.emergency.models import EmergencyRequest


class FacilityTypeEnum(str, enum.Enum):
    HOSPITAL = "HOSPITAL"
    BLOOD_BANK = "BLOOD_BANK"


class InventoryChangeEnum(str, enum.Enum):
    RESTOCK = "RESTOCK"
    EMERGENCY_USE = "EMERGENCY_USE"
    EXPIRY_DISPOSAL = "EXPIRY_DISPOSAL"
    TRANSFER_IN = "TRANSFER_IN"
    TRANSFER_OUT = "TRANSFER_OUT"
    MANUAL_CORRECTION = "MANUAL_CORRECTION"


class BloodInventory(Base):
    __tablename__ = "blood_inventory"
    __table_args__ = (
        UniqueConstraint(
            "facility_type", "facility_id", "blood_type", "component",
            name="uq_blood_inventory_facility_type_component"
        ),
        CheckConstraint("units_available >= 0", name="ck_blood_inventory_units_available_nonneg"),
        CheckConstraint("units_reserved >= 0", name="ck_blood_inventory_units_reserved_nonneg"),
        CheckConstraint("units_reserved <= units_available", name="ck_blood_inventory_reserved_lte_available"),
        CheckConstraint("minimum_threshold >= 0", name="ck_blood_inventory_min_threshold_nonneg"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    facility_type: Mapped[str] = mapped_column(
        ENUM("HOSPITAL", "BLOOD_BANK", name="facility_type_enum", create_type=False),
        nullable=False,
        index=True,
    )
    facility_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    blood_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
    )
    component: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="WHOLE_BLOOD",
    )
    units_available: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    units_reserved: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    minimum_threshold: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5,
    )
    last_restocked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    expiry_date: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
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
    history: Mapped[list["InventoryHistory"]] = relationship(
        "InventoryHistory",
        back_populates="inventory",
        cascade="all, delete-orphan",
    )


class InventoryHistory(Base):
    __tablename__ = "inventory_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    inventory_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("blood_inventory.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    changed_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    change_type: Mapped[str] = mapped_column(
        ENUM(
            "RESTOCK", "EMERGENCY_USE", "EXPIRY_DISPOSAL", "TRANSFER_IN", "TRANSFER_OUT", "MANUAL_CORRECTION",
            name="inventory_change_enum", create_type=False
        ),
        nullable=False,
    )
    units_before: Mapped[int] = mapped_column(Integer, nullable=False)
    units_after: Mapped[int] = mapped_column(Integer, nullable=False)
    units_delta: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    emergency_request_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("emergency_requests.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationships
    inventory: Mapped["BloodInventory"] = relationship("BloodInventory", back_populates="history")
    user: Mapped["User"] = relationship("User")


class BloodBankEmergencyResponse(Base):
    __tablename__ = "blood_bank_emergency_responses"

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
    blood_bank_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("blood_banks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    blood_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )
    units_requested: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    units_committed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="ACCEPTED",
        index=True,
    )
    message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    responded_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
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

    # Relationships
    emergency_request: Mapped["EmergencyRequest"] = relationship("EmergencyRequest")
    blood_bank: Mapped["BloodBank"] = relationship("BloodBank")
    responder: Mapped[Optional["User"]] = relationship("User", foreign_keys=[responded_by])
