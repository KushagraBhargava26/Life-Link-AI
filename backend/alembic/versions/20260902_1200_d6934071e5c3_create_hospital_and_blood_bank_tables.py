# backend/alembic/versions/20260902_1200_d6934071e5c3_create_hospital_and_blood_bank_tables.py
"""create_hospital_and_blood_bank_tables

Revision ID: d6934071e5c3
Revises: c5823960d4b2
Create Date: 2026-09-02 12:00:00.000000+00:00

Architecture Reference: ARCHITECTURE.md Sections 24, 30; DATABASE.md Sections 7, 8
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "d6934071e5c3"
down_revision: Union[str, None] = "c5823960d4b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create hospital_type_enum
    hospital_type_enum = postgresql.ENUM(
        "GOVERNMENT", "PRIVATE", "TRUST", "CLINIC", "SPECIALTY",
        name="hospital_type_enum",
        create_type=False,
    )
    hospital_type_enum.create(op.get_bind(), checkfirst=True)

    # 2. Create hospitals table
    op.create_table(
        "hospitals",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("registration_number", sa.String(length=100), nullable=True),
        sa.Column("type", hospital_type_enum, nullable=False),
        sa.Column("address_line", sa.String(length=255), nullable=False),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("state", sa.String(length=100), nullable=False),
        sa.Column("pincode", sa.String(length=10), nullable=False),
        sa.Column("latitude", sa.Numeric(precision=10, scale=8), nullable=True),
        sa.Column("longitude", sa.Numeric(precision=11, scale=8), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("website", sa.String(length=255), nullable=True),
        sa.Column("bed_count", sa.Integer(), nullable=True),
        sa.Column("has_blood_bank", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("is_verified", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_by", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("registration_number", name="uq_hospitals_registration_number"),
    )
    op.create_index("ix_hospitals_city", "hospitals", ["city"])
    op.create_index("ix_hospitals_is_verified", "hospitals", ["is_verified"])
    op.create_index("ix_hospitals_is_active", "hospitals", ["is_active"])
    op.create_index("ix_hospitals_deleted_at", "hospitals", ["deleted_at"])

    # 3. Create hospital_staff table
    op.create_table(
        "hospital_staff",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("hospital_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("designation", sa.String(length=100), nullable=True),
        sa.Column("is_primary", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("can_manage_inventory", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("can_create_requests", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("joined_at", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["hospital_id"], ["hospitals.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("hospital_id", "user_id", name="uq_hospital_staff_hospital_user"),
    )
    op.create_index("ix_hospital_staff_hospital_id", "hospital_staff", ["hospital_id"])
    op.create_index("ix_hospital_staff_user_id", "hospital_staff", ["user_id"])

    # 4. Create blood_banks table
    op.create_table(
        "blood_banks",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("license_number", sa.String(length=100), nullable=True),
        sa.Column("hospital_id", sa.UUID(), nullable=True),
        sa.Column("address_line", sa.String(length=255), nullable=False),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("state", sa.String(length=100), nullable=False),
        sa.Column("pincode", sa.String(length=10), nullable=False),
        sa.Column("latitude", sa.Numeric(precision=10, scale=8), nullable=True),
        sa.Column("longitude", sa.Numeric(precision=11, scale=8), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("operating_hours", sa.String(length=255), nullable=True),
        sa.Column("is_24_hours", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("accepts_walk_in", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("is_verified", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("manager_user_id", sa.UUID(), nullable=True),
        sa.Column("created_by", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["hospital_id"], ["hospitals.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["manager_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("license_number", name="uq_blood_banks_license_number"),
    )
    op.create_index("ix_blood_banks_city", "blood_banks", ["city"])
    op.create_index("ix_blood_banks_hospital_id", "blood_banks", ["hospital_id"])
    op.create_index("ix_blood_banks_manager_user_id", "blood_banks", ["manager_user_id"])
    op.create_index("ix_blood_banks_is_verified", "blood_banks", ["is_verified"])
    op.create_index("ix_blood_banks_is_active", "blood_banks", ["is_active"])
    op.create_index("ix_blood_banks_deleted_at", "blood_banks", ["deleted_at"])

    # 5. Link emergency_requests foreign keys
    op.create_foreign_key(
        "fk_emergency_requests_hospital_id",
        "emergency_requests",
        "hospitals",
        ["hospital_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_emergency_requests_requested_by",
        "emergency_requests",
        "users",
        ["requested_by"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    # Drop emergency_requests foreign keys
    op.drop_constraint("fk_emergency_requests_requested_by", "emergency_requests", type_="foreignkey")
    op.drop_constraint("fk_emergency_requests_hospital_id", "emergency_requests", type_="foreignkey")

    # Drop blood_banks table
    op.drop_index("ix_blood_banks_deleted_at", table_name="blood_banks")
    op.drop_index("ix_blood_banks_is_active", table_name="blood_banks")
    op.drop_index("ix_blood_banks_is_verified", table_name="blood_banks")
    op.drop_index("ix_blood_banks_manager_user_id", table_name="blood_banks")
    op.drop_index("ix_blood_banks_hospital_id", table_name="blood_banks")
    op.drop_index("ix_blood_banks_city", table_name="blood_banks")
    op.drop_table("blood_banks")

    # Drop hospital_staff table
    op.drop_index("ix_hospital_staff_user_id", table_name="hospital_staff")
    op.drop_index("ix_hospital_staff_hospital_id", table_name="hospital_staff")
    op.drop_table("hospital_staff")

    # Drop hospitals table
    op.drop_index("ix_hospitals_deleted_at", table_name="hospitals")
    op.drop_index("ix_hospitals_is_active", table_name="hospitals")
    op.drop_index("ix_hospitals_is_verified", table_name="hospitals")
    op.drop_index("ix_hospitals_city", table_name="hospitals")
    op.drop_table("hospitals")

    # Drop enum
    sa.Enum(name="hospital_type_enum").drop(op.get_bind(), checkfirst=True)
