# backend/app/modules/notification/service.py
# LifeLink AI — Notification Module Service Layer
# Architecture Reference: ARCHITECTURE.md Section 16 (Backend Architecture)
#
# Rule: Service layer contains ALL business logic.
# - Imports ONLY from: same module's repository.py, notification.service, other module.service
# - FORBIDDEN: importing another module's repository.py or models.py
#
# Phase 1.1: Empty service — no business logic implemented.
# Phase 1.2+: Implement service methods here.

from __future__ import annotations

import structlog

logger = structlog.get_logger(__name__)

import uuid
from sqlalchemy.ext.asyncio import AsyncSession

class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def notify_hospital_donor_accepted(
        self,
        emergency_request_id: uuid.UUID,
        donor_name: str,
        donor_blood_type: str,
        request_number: str,
        hospital_admin_email: str,
    ) -> None:
        """Fires when a donor accepts an emergency request. Logs in-app + prints email simulation."""
        logger.info(
            "NOTIFICATION: donor_accepted_emergency",
            to=hospital_admin_email,
            subject=f"[LifeLink] Donor Accepted: {request_number}",
            donor=donor_name,
            blood_type=donor_blood_type,
            request=request_number,
        )
        # TODO: Integrate SendGrid/Twilio for real email/SMS
        # For now this is logged and visible in docker logs lifelink-backend

    async def notify_donor_request_fulfilled(
        self,
        donor_email: str,
        request_number: str,
    ) -> None:
        logger.info(
            "NOTIFICATION: request_fulfilled",
            to=donor_email,
            message=f"Emergency {request_number} has been fulfilled. Thank you for your contribution!",
        )
