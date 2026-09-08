# backend/app/modules/notification/exceptions.py
# LifeLink AI — Notification Module Custom Exceptions
# Architecture Reference: ARCHITECTURE.md Section 37 (Error Handling Strategy)
#
# All exceptions must inherit from app.core.exceptions.LifeLinkBaseException
# Error codes must be UPPER_SNAKE_CASE (e.g., DONOR_NOT_FOUND)
#
# Phase 1.1: Empty exceptions — defined as modules are implemented.

from __future__ import annotations

from app.core.exceptions import ConflictError, NotFoundError, ValidationError

# Phase 1.2+: Define Notification-specific exceptions here
# Example:
# class NotificationNotFoundError(NotFoundError):
#     def __init__(self, identifier: str) -> None:
#         super().__init__(
#             message=f"Notification not found: {identifier}",
#             code="NOTIFICATION_NOT_FOUND",
#         )
