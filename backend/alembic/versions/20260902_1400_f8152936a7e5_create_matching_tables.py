"""create matching tables

Revision ID: f8152936a7e5
Revises: e7045182f6d4
Create Date: 2026-09-02 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "f8152936a7e5"
down_revision: Union[str, None] = "e7045182f6d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Define enums
match_run_status_enum = postgresql.ENUM(
    "INITIATED",
    "RUNNING",
    "COMPLETED",
    "FAILED",
    "NO_CANDIDATES",
    name="match_run_status_enum",
    create_type=False,
)

match_candidate_type_enum = postgresql.ENUM(
    "DONOR",
    "BLOOD_BANK",
    name="match_candidate_type_enum",
    create_type=False,
)

match_candidate_status_enum = postgresql.ENUM(
    "PROPOSED",
    "SHORTLISTED",
    "DISMISSED",
    name="match_candidate_status_enum",
    create_type=False,
)


def upgrade() -> None:
    # 1. Create Enums
    match_run_status_enum.create(op.get_bind(), checkfirst=True)
    match_candidate_type_enum.create(op.get_bind(), checkfirst=True)
    match_candidate_status_enum.create(op.get_bind(), checkfirst=True)

    # 2. Create match_runs table
    op.create_table(
        "match_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("emergency_request_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("emergency_requests.id", ondelete="CASCADE"), nullable=False),
        sa.Column("run_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", match_run_status_enum, nullable=False, server_default="INITIATED"),
        sa.Column("model_version", sa.String(50), nullable=False, server_default="donor-response-v1"),
        sa.Column("algorithm", sa.String(50), nullable=False, server_default="deterministic_ai_hybrid"),
        sa.Column("search_radius_km", sa.Float(), nullable=False, server_default="50.0"),
        sa.Column("candidates_evaluated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("donors_matched", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("blood_banks_matched", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("execution_duration_ms", sa.Float(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("executed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index("ix_match_runs_emergency_request_id", "match_runs", ["emergency_request_id"])
    op.create_index("ix_match_runs_status", "match_runs", ["status"])
    op.create_index("ix_match_runs_created_at", "match_runs", ["created_at"])
    op.create_unique_constraint("uq_match_runs_request_run_number", "match_runs", ["emergency_request_id", "run_number"])

    # 3. Create match_candidates table
    op.create_table(
        "match_candidates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("match_run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("match_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("emergency_request_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("emergency_requests.id", ondelete="CASCADE"), nullable=False),
        sa.Column("candidate_type", match_candidate_type_enum, nullable=False),
        sa.Column("donor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("donors.id", ondelete="SET NULL"), nullable=True),
        sa.Column("blood_bank_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("blood_banks.id", ondelete="SET NULL"), nullable=True),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("total_score", sa.Float(), nullable=False),
        sa.Column("compatibility_score", sa.Float(), nullable=False),
        sa.Column("proximity_score", sa.Float(), nullable=False),
        sa.Column("availability_score", sa.Float(), nullable=False),
        sa.Column("ai_score", sa.Float(), nullable=True),
        sa.Column("distance_km", sa.Float(), nullable=True),
        sa.Column("units_available", sa.Integer(), nullable=True),
        sa.Column("status", match_candidate_status_enum, nullable=False, server_default="PROPOSED"),
        sa.Column("explanation", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("candidate_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index("ix_match_candidates_match_run_id", "match_candidates", ["match_run_id"])
    op.create_index("ix_match_candidates_emergency_request_id", "match_candidates", ["emergency_request_id"])
    op.create_index("ix_match_candidates_donor_id", "match_candidates", ["donor_id"])
    op.create_index("ix_match_candidates_blood_bank_id", "match_candidates", ["blood_bank_id"])
    op.create_index("ix_match_candidates_status", "match_candidates", ["status"])
    op.create_unique_constraint("uq_match_candidates_run_rank", "match_candidates", ["match_run_id", "rank"])


def downgrade() -> None:
    op.drop_table("match_candidates")
    op.drop_table("match_runs")

    bind = op.get_bind()
    match_candidate_status_enum.drop(bind, checkfirst=True)
    match_candidate_type_enum.drop(bind, checkfirst=True)
    match_run_status_enum.drop(bind, checkfirst=True)
