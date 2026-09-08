# backend/alembic/versions/20260902_1300_e7045182f6d4_create_blood_inventory_tables.py
"""create_blood_inventory_tables

Revision ID: e7045182f6d4
Revises: d6934071e5c3
Create Date: 2026-09-02 13:00:00.000000+00:00

Architecture Reference: ARCHITECTURE.md Section 24, ADR-001; DATABASE.md Section 9
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "e7045182f6d4"
down_revision: Union[str, None] = "d6934071e5c3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create Enums
    facility_type_enum = postgresql.ENUM(
        "HOSPITAL", "BLOOD_BANK",
        name="facility_type_enum",
        create_type=False,
    )
    facility_type_enum.create(op.get_bind(), checkfirst=True)

    inventory_change_enum = postgresql.ENUM(
        "RESTOCK", "EMERGENCY_USE", "EXPIRY_DISPOSAL", "TRANSFER_IN", "TRANSFER_OUT", "MANUAL_CORRECTION",
        name="inventory_change_enum",
        create_type=False,
    )
    inventory_change_enum.create(op.get_bind(), checkfirst=True)

    # 2. Create blood_inventory table
    op.create_table(
        "blood_inventory",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("facility_type", facility_type_enum, nullable=False),
        sa.Column("facility_id", sa.UUID(), nullable=False),
        sa.Column("blood_type", sa.String(length=10), nullable=False),
        sa.Column("component", sa.String(length=30), server_default="WHOLE_BLOOD", nullable=False),
        sa.Column("units_available", sa.Integer(), server_default="0", nullable=False),
        sa.Column("units_reserved", sa.Integer(), server_default="0", nullable=False),
        sa.Column("minimum_threshold", sa.Integer(), server_default="5", nullable=False),
        sa.Column("last_restocked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("facility_type", "facility_id", "blood_type", "component", name="uq_blood_inventory_facility_type_component"),
        sa.CheckConstraint("units_available >= 0", name="ck_blood_inventory_units_available_nonneg"),
        sa.CheckConstraint("units_reserved >= 0", name="ck_blood_inventory_units_reserved_nonneg"),
        sa.CheckConstraint("units_reserved <= units_available", name="ck_blood_inventory_reserved_lte_available"),
        sa.CheckConstraint("minimum_threshold >= 0", name="ck_blood_inventory_min_threshold_nonneg"),
    )
    op.create_index("ix_blood_inventory_facility", "blood_inventory", ["facility_type", "facility_id"])
    op.create_index("ix_blood_inventory_blood_type", "blood_inventory", ["blood_type"])
    op.create_index("ix_blood_inventory_search", "blood_inventory", ["blood_type", "units_available", "facility_type"])
    op.create_index("ix_blood_inventory_deleted_at", "blood_inventory", ["deleted_at"])

    # 3. Create inventory_history table
    op.create_table(
        "inventory_history",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("inventory_id", sa.UUID(), nullable=False),
        sa.Column("changed_by", sa.UUID(), nullable=False),
        sa.Column("change_type", inventory_change_enum, nullable=False),
        sa.Column("units_before", sa.Integer(), nullable=False),
        sa.Column("units_after", sa.Integer(), nullable=False),
        sa.Column("units_delta", sa.Integer(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("emergency_request_id", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["inventory_id"], ["blood_inventory.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["changed_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["emergency_request_id"], ["emergency_requests.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_inventory_history_inventory_id", "inventory_history", ["inventory_id"])
    op.create_index("ix_inventory_history_changed_by", "inventory_history", ["changed_by"])
    op.create_index("ix_inventory_history_emergency_request_id", "inventory_history", ["emergency_request_id"])
    op.create_index("ix_inventory_history_created_at", "inventory_history", ["created_at"])


def downgrade() -> None:
    # Drop inventory_history
    op.drop_index("ix_inventory_history_created_at", table_name="inventory_history")
    op.drop_index("ix_inventory_history_emergency_request_id", table_name="inventory_history")
    op.drop_index("ix_inventory_history_changed_by", table_name="inventory_history")
    op.drop_index("ix_inventory_history_inventory_id", table_name="inventory_history")
    op.drop_table("inventory_history")

    # Drop blood_inventory
    op.drop_index("ix_blood_inventory_deleted_at", table_name="blood_inventory")
    op.drop_index("ix_blood_inventory_search", table_name="blood_inventory")
    op.drop_index("ix_blood_inventory_blood_type", table_name="blood_inventory")
    op.drop_index("ix_blood_inventory_facility", table_name="blood_inventory")
    op.drop_table("blood_inventory")

    # Drop enums
    sa.Enum(name="inventory_change_enum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="facility_type_enum").drop(op.get_bind(), checkfirst=True)
