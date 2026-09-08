# backend/app/modules/auth/exceptions.py
# LifeLink AI — Auth Module Custom Exceptions
# Architecture Reference: ARCHITECTURE.md Section 18 & Section 37

from __future__ import annotations

from typing import Any

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, UnauthorizedError, ValidationError


class InvalidCredentialsError(UnauthorizedError):
    def __init__(self, message: str = "Invalid email or password") -> None:
        super().__init__(message=message, code="AUTH_INVALID_CREDENTIALS")


class TokenExpiredError(UnauthorizedError):
    def __init__(self, message: str = "Authentication token has expired") -> None:
        super().__init__(message=message, code="AUTH_TOKEN_EXPIRED")


class TokenInvalidError(UnauthorizedError):
    def __init__(self, message: str = "Authentication token is invalid or malformed") -> None:
        super().__init__(message=message, code="AUTH_TOKEN_INVALID")


class TokenMissingError(UnauthorizedError):
    def __init__(self, message: str = "Authorization header missing or invalid") -> None:
        super().__init__(message=message, code="AUTH_TOKEN_MISSING")


class UserEmailAlreadyExistsError(ConflictError):
    def __init__(self, email: str) -> None:
        super().__init__(message=f"An account with email '{email}' already exists", code="USER_EMAIL_ALREADY_EXISTS")


class UserNotFoundError(NotFoundError):
    def __init__(self, identifier: str) -> None:
        super().__init__(message=f"User not found: {identifier}", code="USER_NOT_FOUND")


class AccountDisabledError(ForbiddenError):
    def __init__(self, message: str = "User account has been deactivated or suspended") -> None:
        super().__init__(message=message, code="AUTH_ACCOUNT_DISABLED")


class InsufficientRoleError(ForbiddenError):
    def __init__(self, required_roles: list[str]) -> None:
        super().__init__(
            message=f"Access denied. Required role(s): {', '.join(required_roles)}",
            code="AUTH_INSUFFICIENT_ROLE",
        )
