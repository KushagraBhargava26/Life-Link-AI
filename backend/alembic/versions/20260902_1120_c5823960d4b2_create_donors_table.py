# backend/alembic/versions/20260902_1120_c5823960d4b2_create_donors_table.py
"""create_donors_table

Revision ID: c5823960d4b2
Revises: b4712859c3a1
Create Date: 2026-09-02 11:20:00.000000+00:00

Architecture Reference: ARCHITECTURE.md Section 33 & DATABASE.md Section 6
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c5823960d4b2"
down_revision: Union[str, None] = "b4712859c3a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Apply migration — create donors table."""
    op.create_table(
        "donors",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("blood_type", sa.String(length=10), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("gender", sa.String(length=20), nullable=True),
        sa.Column("weight_kg", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("address_line", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("state", sa.String(length=100), nullable=True),
        sa.Column("pincode", sa.String(length=10), nullable=True),
        sa.Column("latitude", sa.Numeric(precision=10, scale=8), nullable=True),
        sa.Column("longitude", sa.Numeric(precision=11, scale=8), nullable=True),
        sa.Column("is_available", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_eligible", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_donation_date", sa.Date(), nullable=True),
        sa.Column("total_donations", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("medical_conditions", sa.Text(), nullable=True),
        sa.Column("fcm_token", sa.String(length=512), nullable=True),
        sa.Column("notification_email", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("notification_push", sa.Boolean(), nullable=False, server_default=sa.text("true")),
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_donors_user_id"),
    )
    op.create_index(op.f("ix_donors_user_id"), "donors", ["user_id"], unique=True)
    op.create_index(op.f("ix_donors_blood_type"), "donors", ["blood_type"], unique=False)
    op.create_index(op.f("ix_donors_city"), "donors", ["city"], unique=False)
    op.create_index(op.f("ix_donors_is_available"), "donors", ["is_available"], unique=False)
    op.create_index(op.f("ix_donors_is_eligible"), "donors", ["is_eligible"], unique=False)
    op.create_index(op.f("ix_donors_deleted_at"), "donors", ["deleted_at"], unique=False)


def downgrade() -> None:
    """Revert migration — drop donors table."""
    op.drop_index(op.f("ix_donors_deleted_at"), table_name="donors")
    op.drop_index(op.f("ix_donors_is_eligible"), table_name="donors")
    op.drop_index(op.f("ix_donors_is_available"), table_name="donors")
    op.drop_index(op.f("ix_donors_city"), table_name="donors")
    op.drop_index(op.f("ix_donors_blood_type"), table_name="donors")
    op.drop_index(op.f("ix_donors_user_id"), table_name="donors")
    op.drop_table("donors")
