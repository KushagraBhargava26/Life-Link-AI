# backend/app/modules/hospital/exceptions.py
# LifeLink AI — Hospital Module Exceptions
# Architecture Reference: ARCHITECTURE.md Section 27; API.md Section 3

from __future__ import annotations

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError


class HospitalNotFoundError(NotFoundError):
    """Raised when a hospital record is not found."""

    def __init__(self, message: str = "Hospital not found") -> None:
        super().__init__(message=message, code="HOSPITAL_NOT_FOUND")


class HospitalAlreadyExistsError(ConflictError):
    """Raised when a hospital with the given registration number already exists."""

    def __init__(self, message: str = "A hospital with this registration number already exists") -> None:
        super().__init__(message=message, code="HOSPITAL_ALREADY_EXISTS")


class HospitalPermissionDeniedError(ForbiddenError):
    """Raised when an operation on a hospital is denied due to permissions."""

    def __init__(self, message: str = "Permission denied for this hospital facility") -> None:
        super().__init__(message=message, code="HOSPITAL_PERMISSION_DENIED")


class HospitalStaffNotFoundError(NotFoundError):
    """Raised when a staff assignment is not found."""

    def __init__(self, message: str = "Hospital staff member not found") -> None:
        super().__init__(message=message, code="HOSPITAL_STAFF_NOT_FOUND")


class HospitalStaffAlreadyExistsError(ConflictError):
    """Raised when a staff member is already assigned to the hospital."""

    def __init__(self, message: str = "User is already registered as staff for this hospital") -> None:
        super().__init__(message=message, code="HOSPITAL_STAFF_ALREADY_EXISTS")
