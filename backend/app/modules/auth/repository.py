# backend/app/modules/auth/repository.py
# LifeLink AI — Auth Module Repository Layer
# Architecture Reference: ARCHITECTURE.md Section 16 & DATABASE.md Section 5

from __future__ import annotations

import datetime
import uuid
from typing import Optional, Sequence

import structlog
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.auth.models import User, UserRole

logger = structlog.get_logger(__name__)


class AuthRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_email(self, email: str) -> Optional[User]:
        clean_email = email.strip().lower()
        stmt = (
            select(User)
            .options(selectinload(User.roles))
            .where(
                func.lower(User.email) == clean_email,
                User.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        stmt = (
            select(User)
            .options(selectinload(User.roles))
            .where(
                User.id == user_id,
                User.deleted_at.is_(None),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, user: User) -> User:
        self.db.add(user)
        await self.db.flush()
        return user

    async def add_role(self, role: UserRole) -> UserRole:
        self.db.add(role)
        await self.db.flush()
        return role

    async def update(self, user: User) -> User:
        await self.db.flush()
        return user

    async def update_last_login(self, user_id: uuid.UUID) -> None:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(last_login_at=datetime.datetime.now(datetime.timezone.utc))
        )
        await self.db.execute(stmt)

