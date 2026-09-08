# backend/app/modules/auth/service.py
# LifeLink AI — Auth Module Service Layer
# Architecture Reference: ARCHITECTURE.md Section 18

from __future__ import annotations

import uuid

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.modules.auth.exceptions import (
    AccountDisabledError,
    InvalidCredentialsError,
    UserEmailAlreadyExistsError,
    UserNotFoundError,
)
from app.modules.auth.models import User, UserRole
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import TokenResponse, UserLoginRequest, UserRegisterRequest, UserResponse

logger = structlog.get_logger(__name__)


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = AuthRepository(db)

    def _to_user_response(self, user: User) -> UserResponse:
        roles_list = [r.role for r in user.roles] if user.roles else []
        return UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            roles=roles_list,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
        )

    async def register(self, data: UserRegisterRequest) -> UserResponse:
        clean_email = data.email.strip().lower()

        # Check for existing email
        existing = await self.repository.get_by_email(clean_email)
        if existing:
            raise UserEmailAlreadyExistsError(clean_email)

        # Hash password
        pwd_hash = hash_password(data.password)

        user = User(
            id=uuid.uuid4(),
            email=clean_email,
            password_hash=pwd_hash,
            first_name=data.first_name.strip(),
            last_name=data.last_name.strip(),
            phone=data.phone.strip() if data.phone else None,
            is_active=True,
            is_verified=False,
        )
        created_user = await self.repository.create_user(user)

        # Assign role
        user_role = UserRole(
            id=uuid.uuid4(),
            user_id=created_user.id,
            role=data.role,
        )
        await self.repository.add_role(user_role)

        await self.db.commit()
        await self.db.refresh(created_user)

        logger.info(
            "user_registered",
            user_id=str(created_user.id),
            email=created_user.email,
            role=data.role,
        )

        return self._to_user_response(created_user)

    async def login(self, data: UserLoginRequest) -> TokenResponse:
        clean_email = data.email.strip().lower()

        user = await self.repository.get_by_email(clean_email)
        if not user:
            raise InvalidCredentialsError()

        if not verify_password(data.password, user.password_hash):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise AccountDisabledError()

        # Update last login timestamp
        await self.repository.update_last_login(user.id)
        await self.db.commit()
        await self.db.refresh(user)

        roles_list = [r.role for r in user.roles] if user.roles else ["DONOR"]
        primary_role = roles_list[0] if roles_list else "DONOR"

        access_token = create_access_token(
            subject=str(user.id),
            role=primary_role,
            additional_claims={"roles": roles_list, "email": user.email},
        )

        logger.info("user_logged_in", user_id=str(user.id), email=user.email)

        return TokenResponse(
            access_token=access_token,
            token_type="Bearer",
            expires_in=900,
            user=self._to_user_response(user),
        )

    async def get_me(self, user_id: uuid.UUID) -> UserResponse:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(str(user_id))
        return self._to_user_response(user)

    async def update_user(self, user: User, data: Any) -> UserResponse:
        if getattr(data, "first_name", None) is not None:
            user.first_name = data.first_name
        if getattr(data, "last_name", None) is not None:
            user.last_name = data.last_name
        if getattr(data, "phone", None) is not None:
            user.phone = data.phone

        await self.repository.update(user)
        await self.db.commit()
        await self.db.refresh(user)
        return self._to_user_response(user)

