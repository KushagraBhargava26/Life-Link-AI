# backend/alembic/script.py.mako
# LifeLink AI — Alembic Migration Script Template
# This template is used when generating new migration files via: alembic revision --autogenerate

"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

Architecture Reference: ARCHITECTURE.md Section 24 (Database Overview)
Rule: Every migration must have a reversible downgrade() function.

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    """Apply migration — add schema changes."""
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """Reverse migration — must be implemented for every migration.
    
    Rule from ARCHITECTURE.md Principle 6:
    'Every database migration must be reversible.'
    """
    ${downgrades if downgrades else "pass"}
