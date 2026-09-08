# backend/app/modules/notification/adapters/smtp_adapter.py
# LifeLink AI — SMTP Email Adapter
# Architecture Reference: ARCHITECTURE.md Section 27 (Third-Party Services)
#
# Wraps aiosmtplib for async email delivery.
# Architecture Rule: All third-party services must be wrapped in adapter classes.
#
# Phase 1.1: Placeholder adapter — no SMTP calls implemented.
# Phase 1.2+: Implement email delivery.

from __future__ import annotations

import structlog

logger = structlog.get_logger(__name__)


class SMTPAdapter:
    """
    SMTP email delivery adapter.

    Architecture Reference: ARCHITECTURE.md Section 19 (Notification Architecture)
    Wraps aiosmtplib. Only this class may import aiosmtplib.

    Phase 1.1: Placeholder.
    Phase 1.2+: Implement send_email() using aiosmtplib.
    """

    async def send_email(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        html_body: str,
        text_body: str | None = None,
    ) -> bool:
        """
        Send a transactional email.

        Phase 1.1: Placeholder — raises NotImplementedError.

        Args:
            to_email: Recipient email address.
            to_name: Recipient display name.
            subject: Email subject line.
            html_body: HTML email body.
            text_body: Plain-text fallback body.

        Returns:
            True if email was sent successfully.
        """
        raise NotImplementedError("SMTP email delivery not yet implemented — Phase 1.2")
