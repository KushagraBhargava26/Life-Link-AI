# backend/app/modules/notification/adapters/firebase_adapter.py
# LifeLink AI — Firebase Cloud Messaging Adapter
# Architecture Reference: ARCHITECTURE.md Section 27 (Third-Party Services)
#
# Wraps Firebase Admin SDK — the rest of the codebase never imports Firebase directly.
# Architecture Rule: All third-party services must be wrapped in adapter classes.
#
# Phase 1.1: Placeholder adapter — no Firebase calls implemented.
# Phase 1.2+: Implement push notification dispatch.

from __future__ import annotations

import structlog

logger = structlog.get_logger(__name__)


class FirebaseAdapter:
    """
    Firebase Cloud Messaging adapter.

    Architecture Reference: ARCHITECTURE.md Section 19 (Notification Architecture)
    Wraps firebase_admin SDK. Only this class may import firebase_admin.

    Phase 1.1: Placeholder.
    Phase 1.2+: Initialize Firebase app and implement send_notification().
    """

    def __init__(self) -> None:
        # Phase 1.2+: Initialize Firebase Admin SDK from FIREBASE_CREDENTIALS_JSON
        # from app.config import settings
        # import firebase_admin
        # from firebase_admin import credentials, messaging
        self._initialized = False
        logger.info("FirebaseAdapter created (not yet initialized)")

    async def send_notification(
        self,
        device_token: str,
        title: str,
        body: str,
        data: dict[str, str] | None = None,
    ) -> bool:
        """
        Send a push notification to a single device.

        Phase 1.1: Placeholder — raises NotImplementedError.

        Args:
            device_token: FCM device registration token.
            title: Notification title.
            body: Notification body text.
            data: Optional key-value data payload.

        Returns:
            True if notification was sent successfully.
        """
        raise NotImplementedError("Firebase push notifications not yet implemented — Phase 1.2")

    async def send_multicast(
        self,
        device_tokens: list[str],
        title: str,
        body: str,
        data: dict[str, str] | None = None,
    ) -> dict[str, int]:
        """
        Send a push notification to multiple devices simultaneously.

        Phase 1.1: Placeholder — raises NotImplementedError.

        Returns:
            dict with 'success_count' and 'failure_count' keys.
        """
        raise NotImplementedError("Firebase multicast not yet implemented — Phase 1.2")
