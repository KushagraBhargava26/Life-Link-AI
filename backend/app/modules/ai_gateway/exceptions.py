# backend/app/modules/ai_gateway/exceptions.py
# LifeLink AI — Ai_Gateway Module Custom Exceptions
# Architecture Reference: ARCHITECTURE.md Section 37 (Error Handling Strategy)
#
# All exceptions must inherit from app.core.exceptions.LifeLinkBaseException
# Error codes must be UPPER_SNAKE_CASE (e.g., DONOR_NOT_FOUND)
#
# Phase 1.1: Empty exceptions — defined as modules are implemented.

from __future__ import annotations

from app.core.exceptions import ConflictError, NotFoundError, ValidationError

# Phase 1.2+: Define Ai_Gateway-specific exceptions here
# Example:
# class Ai_GatewayNotFoundError(NotFoundError):
#     def __init__(self, identifier: str) -> None:
#         super().__init__(
#             message=f"Ai_Gateway not found: {identifier}",
#             code="AI_GATEWAY_NOT_FOUND",
#         )
