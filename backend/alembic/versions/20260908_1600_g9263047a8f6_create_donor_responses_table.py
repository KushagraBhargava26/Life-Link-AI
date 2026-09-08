"""create donor emergency responses table

Revision ID: g9263047a8f6
Revises: f8152936a7e5
Create Date: 2026-09-08 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "g9263047a8f6"
down_revision: Union[str, None] = "f8152936a7e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "donor_emergency_responses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "emergency_request_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("emergency_requests.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "donor_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("donors.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(20), nullable=False, server_default="ACCEPTED"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "responded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
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
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index(
        "ix_donor_emergency_responses_emergency_request_id",
        "donor_emergency_responses",
        ["emergency_request_id"],
    )
    op.create_index(
        "ix_donor_emergency_responses_donor_id",
        "donor_emergency_responses",
        ["donor_id"],
    )
    op.create_index(
        "ix_donor_emergency_responses_status",
        "donor_emergency_responses",
        ["status"],
    )
    op.create_unique_constraint(
        "uq_donor_emergency_responses_req_donor",
        "donor_emergency_responses",
        ["emergency_request_id", "donor_id"],
    )


def downgrade() -> None:
    op.drop_table("donor_emergency_responses")
