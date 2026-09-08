# backend/app/database.py
# LifeLink AI — SQLAlchemy Async Database Engine and Session Factory
# Architecture Reference: ARCHITECTURE.md Section 24 (Database Overview)
#
# Uses asyncpg driver for all database operations.
# Connection pooling configured for MVP single-VPS deployment.
# All database access goes through this module — never raw connections.

from __future__ import annotations

from typing import AsyncGenerator

import structlog
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# SQLAlchemy Base — All ORM models inherit from this
# Architecture Reference: ARCHITECTURE.md Section 24 (Database Standards)
# ---------------------------------------------------------------------------
class Base(DeclarativeBase):
    """
    SQLAlchemy declarative base for all ORM models.

    Every model must inherit from this class.
    Provides type-level metadata registration for Alembic auto-detection.

    Standard column conventions (per ARCHITECTURE.md Section 24):
    - id: UUID primary key
    - created_at: timestamp with timezone
    - updated_at: timestamp with timezone
    - deleted_at: soft delete timestamp (None = not deleted)
    """

    pass


# ---------------------------------------------------------------------------
# Async Engine
# ---------------------------------------------------------------------------
# Engine is module-level but initialized lazily to support testing overrides.
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _create_engine() -> AsyncEngine:
    """Create and configure the async SQLAlchemy engine."""
    return create_async_engine(
        settings.DATABASE_URL,
        pool_size=settings.DB_POOL_MIN,
        max_overflow=settings.DB_POOL_MAX - settings.DB_POOL_MIN,
        pool_pre_ping=True,           # Verify connections before use
        pool_recycle=3600,            # Recycle connections after 1 hour
        echo=settings.IS_DEVELOPMENT, # Log SQL queries in development only
        # Future: enable query statistics for performance monitoring
    )


def get_engine() -> AsyncEngine:
    """Return the singleton async database engine."""
    global _engine
    if _engine is None:
        _engine = _create_engine()
        logger.info(
            "Database engine created",
            pool_size=settings.DB_POOL_MIN,
            max_overflow=settings.DB_POOL_MAX - settings.DB_POOL_MIN,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the singleton async session factory."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,    # Prevents lazy-loading issues after commit
            autocommit=False,
            autoflush=False,
        )
    return _session_factory


# ---------------------------------------------------------------------------
# Database Session Dependency
# Used in FastAPI route handlers via: db: AsyncSession = Depends(get_db)
# ---------------------------------------------------------------------------
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an async database session.

    Ensures the session is always properly closed, even on exceptions.
    Rollback is automatic via the context manager.

    Usage in route handlers:
        @router.get("/example")
        async def example(db: AsyncSession = Depends(get_db)):
            ...
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ---------------------------------------------------------------------------
# Lifecycle Functions — called from app/main.py lifespan
# ---------------------------------------------------------------------------
async def init_db() -> None:
    """
    Initialize database connection pool on application startup.

    Called from the FastAPI lifespan context manager in main.py.
    Phase 1.1: Placeholder — connection created on first use.
    Phase 1.2+: Will run PostGIS extension check and initial health query.
    """
    engine = get_engine()
    logger.info("Database connection pool initialized", url=settings.DATABASE_URL.split("@")[-1])


async def close_db() -> None:
    """
    Dispose the database connection pool on application shutdown.

    Called from the FastAPI lifespan context manager in main.py.
    """
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("Database connection pool closed")
