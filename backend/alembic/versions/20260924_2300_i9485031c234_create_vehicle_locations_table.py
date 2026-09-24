"""Phase 1.8 — Create vehicle_locations table for live GPS telemetry

Revision ID: i9485031c234
Revises: h8374920b123
Create Date: 2026-09-24 23:00:00.000000

"""
from __future__ import annotations
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "i9485031c234"
down_revision = "h8374920b123"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "vehicle_locations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("request_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("heading", sa.Float(), nullable=True),
        sa.Column("speed_kmh", sa.Float(), nullable=True),
        sa.Column("status_note", sa.String(200), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["request_id"],
            ["emergency_requests.id"],
            name="fk_vehicle_locations_request_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_vehicle_locations_request_id",
        "vehicle_locations",
        ["request_id"],
    )
    op.create_index(
        "ix_vehicle_locations_recorded_at",
        "vehicle_locations",
        ["recorded_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_vehicle_locations_recorded_at", table_name="vehicle_locations")
    op.drop_index("ix_vehicle_locations_request_id", table_name="vehicle_locations")
    op.drop_table("vehicle_locations")
