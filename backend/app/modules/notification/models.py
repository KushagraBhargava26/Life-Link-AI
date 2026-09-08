# backend/app/modules/notification/models.py
# LifeLink AI — Notification Module SQLAlchemy ORM Models
# Architecture Reference: ARCHITECTURE.md Section 24 (Database Overview)
# Full schema defined in DATABASE.md
#
# Rules:
# - All models inherit from app.database.Base
# - Every table has: id (UUID), created_at, updated_at, deleted_at (soft delete)
# - No raw SQL — always use SQLAlchemy ORM
#
# Phase 1.1: Empty models — no tables defined yet.
# Phase 1.2+: Define SQLAlchemy ORM models here based on DATABASE.md.

from __future__ import annotations

from app.database import Base

# Phase 1.2+: Define Notification ORM models here
# Each model must inherit from Base and include standard columns
