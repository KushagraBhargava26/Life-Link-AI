# backend/app/core/security.py
# LifeLink AI — Security: JWT and Password Hashing
# Architecture Reference: ARCHITECTURE.md Section 18 (Authentication Architecture)

from __future__ import annotations

import datetime
import uuid
import bcrypt
import structlog
from jose import ExpiredSignatureError, JWTError, jwt

from app.config import settings
from app.modules.auth.exceptions import TokenExpiredError, TokenInvalidError

logger = structlog.get_logger(__name__)


def hash_password(plain_password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    pwd_bytes = plain_password.encode("utf-8")[:72]
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


get_password_hash = hash_password



def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a stored bcrypt hash."""
    pwd_bytes = plain_password.encode("utf-8")[:72]
    return bcrypt.checkpw(pwd_bytes, hashed_password.encode("utf-8"))


def create_access_token(
    subject: str,
    role: str = "DONOR",
    additional_claims: dict[str, Any] | None = None,
) -> str:
    """
    Create a JWT access token.
    - Algorithm: HS256
    - TTL: settings.ACCESS_TOKEN_TTL (15 minutes)
    - Claims: sub (user_id), role, type="access", exp, iat
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    expire = now + datetime.timedelta(seconds=settings.ACCESS_TOKEN_TTL)
    
    claims: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    if additional_claims:
        claims.update(additional_claims)

    return jwt.encode(claims, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str) -> str:
    """
    Create a JWT refresh token.
    - TTL: settings.REFRESH_TOKEN_TTL (7 days)
    - Claims: sub (user_id), type="refresh", jti, exp, iat
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    expire = now + datetime.timedelta(seconds=settings.REFRESH_TOKEN_TTL)

    claims: dict[str, Any] = {
        "sub": subject,
        "type": "refresh",
        "jti": str(uuid.uuid4()),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }

    return jwt.encode(claims, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_access_token(token: str) -> dict[str, Any]:
    """
    Decode and verify a JWT access token.
    Raises TokenExpiredError or TokenInvalidError.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != "access":
            raise TokenInvalidError("Token is not an access token")
        return payload
    except ExpiredSignatureError:
        raise TokenExpiredError("Access token has expired")
    except JWTError:
        raise TokenInvalidError("Invalid access token")


def verify_refresh_token(token: str) -> dict[str, Any]:
    """
    Decode and verify a JWT refresh token.
    Raises TokenExpiredError or TokenInvalidError.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != "refresh":
            raise TokenInvalidError("Token is not a refresh token")
        return payload
    except ExpiredSignatureError:
        raise TokenExpiredError("Refresh token has expired")
    except JWTError:
        raise TokenInvalidError("Invalid refresh token")
