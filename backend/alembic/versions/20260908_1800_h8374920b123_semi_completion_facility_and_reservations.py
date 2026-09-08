"""semi completion facility licensing, status, and blood bank emergency responses

Revision ID: h8374920b123
Revises: g9263047a8f6
Create Date: 2026-09-08 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "h8374920b123"
down_revision: Union[str, None] = "g9263047a8f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add licensing metadata and status to hospitals
    op.add_column("hospitals", sa.Column("license_issue_date", sa.Date(), nullable=True))
    op.add_column("hospitals", sa.Column("license_expiry_date", sa.Date(), nullable=True))
    op.add_column("hospitals", sa.Column("certificate_url", sa.String(512), nullable=True))
    op.add_column("hospitals", sa.Column("status", sa.String(20), nullable=False, server_default="ACTIVE"))
    op.create_index("ix_hospitals_status", "hospitals", ["status"])

    # 2. Add licensing metadata and status to blood_banks
    op.add_column("blood_banks", sa.Column("license_issue_date", sa.Date(), nullable=True))
    op.add_column("blood_banks", sa.Column("license_expiry_date", sa.Date(), nullable=True))
    op.add_column("blood_banks", sa.Column("certificate_url", sa.String(512), nullable=True))
    op.add_column("blood_banks", sa.Column("status", sa.String(20), nullable=False, server_default="ACTIVE"))
    op.create_index("ix_blood_banks_status", "blood_banks", ["status"])

    # 3. Create blood_bank_emergency_responses table
    op.create_table(
        "blood_bank_emergency_responses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "emergency_request_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("emergency_requests.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "blood_bank_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("blood_banks.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("blood_type", sa.String(10), nullable=False),
        sa.Column("units_requested", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("units_committed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(30), nullable=False, server_default="ACCEPTED"),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column(
            "responded_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
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
    )

    op.create_index(
        "ix_bb_emergency_responses_req_id",
        "blood_bank_emergency_responses",
        ["emergency_request_id"],
    )
    op.create_index(
        "ix_bb_emergency_responses_bank_id",
        "blood_bank_emergency_responses",
        ["blood_bank_id"],
    )
    op.create_index(
        "ix_bb_emergency_responses_status",
        "blood_bank_emergency_responses",
        ["status"],
    )
    op.create_unique_constraint(
        "uq_bb_response_req_bank",
        "blood_bank_emergency_responses",
        ["emergency_request_id", "blood_bank_id"],
    )


def downgrade() -> None:
    op.drop_table("blood_bank_emergency_responses")
    op.drop_index("ix_blood_banks_status", table_name="blood_banks")
    op.drop_column("blood_banks", "status")
    op.drop_column("blood_banks", "certificate_url")
    op.drop_column("blood_banks", "license_expiry_date")
    op.drop_column("blood_banks", "license_issue_date")

    op.drop_index("ix_hospitals_status", table_name="hospitals")
    op.drop_column("hospitals", "status")
    op.drop_column("hospitals", "certificate_url")
    op.drop_column("hospitals", "license_expiry_date")
    op.drop_column("hospitals", "license_issue_date")
