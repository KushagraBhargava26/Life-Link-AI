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

# Phase 1.2+: Implement NotificationService class here
