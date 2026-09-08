# backend/alembic/versions/20260902_1025_a2370546e98c_create_emergency_requests_table.py
"""create_emergency_requests_table

Revision ID: a2370546e98c
Revises:
Create Date: 2026-09-02 10:25:26.701675+00:00

Architecture Reference: ARCHITECTURE.md Section 24 (Database Overview)
Rule: Every migration must have a reversible downgrade function.
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a2370546e98c"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Apply migration — add emergency_requests table."""
    op.create_table(
        "emergency_requests",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("request_number", sa.String(length=20), nullable=False),
        sa.Column("requested_by", sa.UUID(), nullable=True),
        sa.Column("patient_name", sa.String(length=200), nullable=True),
        sa.Column("patient_age", sa.Integer(), nullable=True),
        sa.Column("blood_type", sa.String(length=10), nullable=False),
        sa.Column("units_required", sa.Integer(), nullable=False),
        sa.Column("units_fulfilled", sa.Integer(), nullable=False),
        sa.Column("urgency_level", sa.String(length=20), nullable=False),
        sa.Column("hospital_name", sa.String(length=200), nullable=True),
        sa.Column("hospital_id", sa.UUID(), nullable=True),
        sa.Column("facility_address", sa.Text(), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("latitude", sa.Numeric(precision=10, scale=8), nullable=True),
        sa.Column("longitude", sa.Numeric(precision=11, scale=8), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("ai_assisted", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("fulfilled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancellation_reason", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_emergency_requests_blood_type"),
        "emergency_requests",
        ["blood_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_emergency_requests_city"),
        "emergency_requests",
        ["city"],
        unique=False,
    )
    op.create_index(
        op.f("ix_emergency_requests_deleted_at"),
        "emergency_requests",
        ["deleted_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_emergency_requests_hospital_id"),
        "emergency_requests",
        ["hospital_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_emergency_requests_request_number"),
        "emergency_requests",
        ["request_number"],
        unique=True,
    )
    op.create_index(
        op.f("ix_emergency_requests_requested_by"),
        "emergency_requests",
        ["requested_by"],
        unique=False,
    )
    op.create_index(
        op.f("ix_emergency_requests_status"),
        "emergency_requests",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_emergency_requests_urgency_level"),
        "emergency_requests",
        ["urgency_level"],
        unique=False,
    )


def downgrade() -> None:
    """Revert migration — drop emergency_requests table."""
    op.drop_index(op.f("ix_emergency_requests_urgency_level"), table_name="emergency_requests")
    op.drop_index(op.f("ix_emergency_requests_status"), table_name="emergency_requests")
    op.drop_index(op.f("ix_emergency_requests_requested_by"), table_name="emergency_requests")
    op.drop_index(op.f("ix_emergency_requests_request_number"), table_name="emergency_requests")
    op.drop_index(op.f("ix_emergency_requests_hospital_id"), table_name="emergency_requests")
    op.drop_index(op.f("ix_emergency_requests_deleted_at"), table_name="emergency_requests")
    op.drop_index(op.f("ix_emergency_requests_city"), table_name="emergency_requests")
    op.drop_index(op.f("ix_emergency_requests_blood_type"), table_name="emergency_requests")
    op.drop_table("emergency_requests")
