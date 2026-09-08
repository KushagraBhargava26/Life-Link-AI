# backend/app/modules/blood_bank/exceptions.py
# LifeLink AI — Blood Bank Module Exceptions
# Architecture Reference: ARCHITECTURE.md Section 27; API.md Section 3

from __future__ import annotations

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError


class BloodBankNotFoundError(NotFoundError):
    """Raised when a blood bank record is not found."""

    def __init__(self, message: str = "Blood bank not found") -> None:
        super().__init__(message=message, code="BLOOD_BANK_NOT_FOUND")


class BloodBankAlreadyExistsError(ConflictError):
    """Raised when a blood bank with the given license number already exists."""

    def __init__(self, message: str = "A blood bank with this license number already exists") -> None:
        super().__init__(message=message, code="BLOOD_BANK_ALREADY_EXISTS")


class BloodBankPermissionDeniedError(ForbiddenError):
    """Raised when an action on a blood bank facility is forbidden."""

    def __init__(self, message: str = "Permission denied for this blood bank facility") -> None:
        super().__init__(message=message, code="BLOOD_BANK_PERMISSION_DENIED")
