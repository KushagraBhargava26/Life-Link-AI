# backend/alembic/env.py
# LifeLink AI — Alembic Migration Environment
# Architecture Reference: ARCHITECTURE.md Section 24 (Database Overview)
#
# This file configures Alembic to use the async SQLAlchemy engine.
# All database schema changes must go through Alembic.
# Never run manual SQL in production.

from __future__ import annotations

import asyncio
import os
import sys
from logging.config import fileConfig
from typing import Any

# Ensure project root (/app) is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# ---------------------------------------------------------------------------
# Alembic Config Object
# Provides access to the values within the .ini file in use.
# ---------------------------------------------------------------------------
config = context.config

# ---------------------------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------------------------
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------------
# Metadata Target — Import all models here so Alembic can auto-detect changes
# ---------------------------------------------------------------------------
from app.database import Base
from app.modules.emergency.models import EmergencyRequest  # noqa: F401
from app.modules.auth.models import User, UserRole  # noqa: F401
from app.modules.donor.models import Donor  # noqa: F401
from app.modules.hospital.models import Hospital, HospitalStaff  # noqa: F401
from app.modules.blood_bank.models import BloodBank  # noqa: F401
from app.modules.inventory.models import BloodInventory, InventoryHistory  # noqa: F401
from app.modules.matching.models import MatchRun, MatchCandidate  # noqa: F401

target_metadata = Base.metadata

# ---------------------------------------------------------------------------
# Override SQLAlchemy URL from environment variable
# Prevents hardcoding credentials in alembic.ini
# ---------------------------------------------------------------------------
def get_database_url() -> str:
    """Return the database URL from settings or environment variable."""
    from app.config import settings
    return str(settings.DATABASE_URL)


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine.
    Useful for generating SQL scripts without connecting to the DB.
    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Execute migrations using the provided connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Run migrations in 'online' mode using an async engine.

    Uses asyncpg driver for connection as specified in ARCHITECTURE.md.
    """
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_database_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # No connection pooling for migrations
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Entry point for online migration execution."""
    asyncio.run(run_async_migrations())


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
