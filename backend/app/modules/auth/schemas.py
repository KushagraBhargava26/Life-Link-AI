# backend/app/modules/auth/schemas.py
# LifeLink AI — Auth Module Pydantic v2 Schemas
# Architecture Reference: ARCHITECTURE.md Section 18 & Section 23

from __future__ import annotations

import re
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


VALID_ROLES = {
    "SUPER_ADMIN",
    "ADMIN",
    "HOSPITAL_ADMIN",
    "HOSPITAL_STAFF",
    "BLOOD_BANK_MANAGER",
    "BLOOD_BANK_STAFF",
    "DONOR",
    "PATIENT",
    "GOVERNMENT_ANALYST",
}

VALID_PUBLIC_ROLES = {
    "DONOR",
    "PATIENT",
    "HOSPITAL_ADMIN",
    "HOSPITAL_STAFF",
    "BLOOD_BANK_MANAGER",
    "BLOOD_BANK_STAFF",
}


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128, description="Password (min 8 chars, 1 upper, 1 digit, 1 special)")
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    role: str = Field(default="DONOR", description="Primary role to assign")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit.")
        special_chars = set("!@#$%^&*(),.?\":{}|<>-_+=~[]/`")
        if not any(c in special_chars for c in v):
            raise ValueError("Password must contain at least one special character.")
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        clean = v.strip().upper()
        if clean not in VALID_ROLES:
            raise ValueError(f"Invalid registration role '{v}'. Allowed roles: {', '.join(sorted(VALID_ROLES))}")
        return clean


    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Name cannot be empty.")
        if re.search(r"\d", clean):
            raise ValueError("Name cannot contain numbers.")
        if not re.match(r"^[a-zA-Z\s\-\'\.]+$", clean):
            raise ValueError("Name contains invalid characters.")
        return clean

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        clean = v.strip()
        if not clean:
            return None
        digits = re.sub(r"\D", "", clean)
        if len(digits) < 7 or len(digits) > 15:
            raise ValueError("Phone number must contain between 7 and 15 digits.")
        if not re.match(r"^\+?[0-9\s\-()]{7,20}$", clean):
            raise ValueError("Invalid phone number format.")
        return clean


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class UserUpdateRequest(BaseModel):
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        clean = v.strip()
        if not clean:
            raise ValueError("Name cannot be empty.")
        if re.search(r"\d", clean):
            raise ValueError("Name cannot contain numbers.")
        if not re.match(r"^[a-zA-Z\s\-\'\.]+$", clean):
            raise ValueError("Name contains invalid characters.")
        return clean

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        clean = v.strip()
        if not clean:
            return None
        digits = re.sub(r"\D", "", clean)
        if len(digits) < 7 or len(digits) > 15:
            raise ValueError("Phone number must contain between 7 and 15 digits.")
        if not re.match(r"^\+?[0-9\s\-()]{7,20}$", clean):
            raise ValueError("Invalid phone number format.")
        return clean


class UserResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    roles: list[str] = Field(default_factory=list)
    is_active: bool
    is_verified: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 900
    user: UserResponse
