# backend/app/modules/notification/router.py
# LifeLink AI — Notification Module Router
# Architecture Reference: ARCHITECTURE.md Section 22 (Module Breakdown)
#
# Rule: Router contains FastAPI route definitions ONLY — no business logic.
# All business logic must be delegated to notification.service
#
# Phase 1.1: Empty router — no endpoints implemented.
# Phase 1.2+: Add endpoint definitions here.

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()

# Phase 1.2+: Add route handlers here
# Example:
# @router.get("/")
# async def list_notifications(
#     db: AsyncSession = Depends(get_db),
#     current_user: UserSchema = Depends(get_current_user),
# ) -> ...
