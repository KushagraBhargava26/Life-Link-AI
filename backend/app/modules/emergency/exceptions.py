# backend/app/modules/emergency/exceptions.py
# LifeLink AI — Emergency Module Custom Exceptions
# Architecture Reference: ARCHITECTURE.md Section 37 (Error Handling Strategy)
#
# All exceptions must inherit from app.core.exceptions.LifeLinkBaseException
# Error codes must be UPPER_SNAKE_CASE (e.g., DONOR_NOT_FOUND)
#
# Phase 1.1: Empty exceptions — defined as modules are implemented.

from __future__ import annotations

from app.core.exceptions import ConflictError, NotFoundError, ValidationError


class EmergencyNotFoundError(NotFoundError):
    def __init__(self, identifier: str) -> None:
        super().__init__(
            message=f"Emergency request not found: {identifier}",
            code="EMERGENCY_NOT_FOUND",
        )


class InvalidBloodTypeError(ValidationError):
    def __init__(self, blood_type: str) -> None:
        super().__init__(
            message=f"Invalid blood type provided: {blood_type}",
            code="BLOOD_TYPE_INVALID",
        )


class EmergencyAlreadyFulfilledError(ConflictError):
    def __init__(self, request_number: str) -> None:
        super().__init__(
            message=f"Emergency request {request_number} is already fulfilled or cancelled",
            code="EMERGENCY_ALREADY_FULFILLED",
        )
