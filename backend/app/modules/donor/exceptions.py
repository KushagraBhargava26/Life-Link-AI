# backend/app/modules/donor/exceptions.py
# LifeLink AI — Donor Module Custom Exceptions
# Architecture Reference: ARCHITECTURE.md Section 37

from __future__ import annotations

from app.core.exceptions import ConflictError, NotFoundError, ValidationError


class DonorNotFoundError(NotFoundError):
    def __init__(self, identifier: str = "current user") -> None:
        super().__init__(message=f"Donor profile not found for {identifier}", code="DONOR_NOT_FOUND")


class DonorProfileAlreadyExistsError(ConflictError):
    def __init__(self) -> None:
        super().__init__(message="A donor profile already exists for this account", code="DONOR_PROFILE_EXISTS")
