# backend/app/modules/auth/router.py
# LifeLink AI — Auth Module Router
# Architecture Reference: ARCHITECTURE.md Section 18 & API.md Section 6

from __future__ import annotations

import datetime
from typing import Any

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_active_user
from app.modules.auth.schemas import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
    UserUpdateRequest,
)
from app.modules.auth.service import AuthService


router = APIRouter()


def _format_success(data: Any, message: str = "Operation successful") -> dict[str, Any]:
    return {
        "success": True,
        "data": data,
        "message": message,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


@router.post(
    "/register",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    data: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = AuthService(db)
    user_resp = await service.register(data)
    return _format_success(
        data=user_resp.model_dump(mode="json"),
        message=f"User account {user_resp.email} registered successfully",
    )


@router.post(
    "/login",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Authenticate and receive JWT token",
)
async def login(
    data: UserLoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = AuthService(db)
    token_resp = await service.login(data)

    # Set HTTP-only refresh token cookie
    response.set_cookie(
        key="lifelink_refresh",
        value=token_resp.access_token,
        httponly=True,
        samesite="lax",
        max_age=604800,
        path="/api/v1/auth",
    )

    return _format_success(
        data=token_resp.model_dump(mode="json"),
        message="Login successful",
    )


@router.get(
    "/me",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user profile",
)
async def get_me(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = AuthService(db)
    user_resp = service._to_user_response(current_user)
    return _format_success(data=user_resp.model_dump(mode="json"))


@router.patch(
    "/me",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Update current authenticated user profile",
)
async def update_me(
    data: UserUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    service = AuthService(db)
    user_resp = await service.update_user(current_user, data)
    return _format_success(
        data=user_resp.model_dump(mode="json"),
        message="Profile updated successfully",
    )



@router.post(
    "/logout",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Logout and invalidate session",
)
async def logout(
    response: Response,
    current_user: User = Depends(get_current_active_user),
) -> dict[str, Any]:
    response.delete_cookie(key="lifelink_refresh", path="/api/v1/auth")
    return _format_success(
        data={"user_id": str(current_user.id)},
        message="Logged out successfully",
    )
