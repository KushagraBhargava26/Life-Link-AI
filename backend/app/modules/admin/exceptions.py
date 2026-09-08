# backend/app/modules/admin/exceptions.py
# LifeLink AI — Admin Module Custom Exceptions
# Architecture Reference: ARCHITECTURE.md Section 37 (Error Handling Strategy)

from __future__ import annotations

from app.core.exceptions import NotFoundError


class HospitalNotFoundError(NotFoundError):
    def __init__(self, identifier: str) -> None:
        super().__init__(
            message=f"Hospital not found: {identifier}",
            code="HOSPITAL_NOT_FOUND",
        )


class BloodBankNotFoundError(NotFoundError):
    def __init__(self, identifier: str) -> None:
        super().__init__(
            message=f"Blood bank not found: {identifier}",
            code="BLOOD_BANK_NOT_FOUND",
        )

