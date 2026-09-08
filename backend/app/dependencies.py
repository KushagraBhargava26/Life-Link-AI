# backend/app/dependencies.py
# LifeLink AI — Shared FastAPI Dependency Functions
# Architecture Reference: ARCHITECTURE.md Section 16 & Section 18

from __future__ import annotations

import uuid
from typing import Any, Callable

import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_access_token
from app.database import get_db
from app.modules.auth.exceptions import (
    AccountDisabledError,
    InsufficientRoleError,
    TokenMissingError,
    UserNotFoundError,
)
from app.modules.auth.models import User
from app.modules.auth.repository import AuthRepository

logger = structlog.get_logger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Validates JWT Bearer token and returns the current User object from PostgreSQL.
    """
    if not credentials or not credentials.credentials:
        raise TokenMissingError()

    token = credentials.credentials
    payload = verify_access_token(token)

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UserNotFoundError("Invalid token subject")

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise UserNotFoundError("Invalid user UUID in token")

    repo = AuthRepository(db)
    user = await repo.get_by_id(user_uuid)
    if not user:
        raise UserNotFoundError(user_id_str)

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Ensures current user is active (not deactivated or suspended).
    """
    if not current_user.is_active:
        raise AccountDisabledError()
    return current_user


def require_role(*allowed_roles: str) -> Callable[..., Any]:
    """
    Role-Based Access Control (RBAC) dependency factory.
    SUPER_ADMIN always satisfies all requirements.
    """
    async def role_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        user_roles = {r.role.upper() for r in current_user.roles}
        allowed = {r.upper() for r in allowed_roles}

        # Super admin bypass
        if "SUPER_ADMIN" in user_roles:
            return current_user

        if not user_roles.intersection(allowed):
            raise InsufficientRoleError(list(allowed_roles))

        return current_user

    return role_checker


# Role shortcut dependencies
require_admin = require_role("ADMIN", "SUPER_ADMIN")
require_hospital_staff = require_role("HOSPITAL_ADMIN", "HOSPITAL_STAFF")
require_blood_bank_staff = require_role("BLOOD_BANK_MANAGER", "BLOOD_BANK_STAFF")
require_donor = require_role("DONOR")
require_patient = require_role("PATIENT")
require_government = require_role("GOVERNMENT_ANALYST")


async def get_pagination(
    page: int = 1,
    page_size: int = 20,
) -> dict[str, int]:
    """Common pagination parameters dependency."""
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Page number must be >= 1",
        )
    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Page size must be between 1 and 100",
        )
    return {
        "offset": (page - 1) * page_size,
        "limit": page_size,
    }
