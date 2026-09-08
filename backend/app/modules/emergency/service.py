# backend/app/modules/emergency/service.py
# LifeLink AI — Emergency Module Service Layer
# Architecture Reference: ARCHITECTURE.md Section 16 (Backend Architecture)
#
# Rule: Service layer contains ALL business logic.
# - Imports ONLY from: same module's repository.py, notification.service, other module.service
# - FORBIDDEN: importing another module's repository.py or models.py
#
# Phase 1.1: Empty service — no business logic implemented.
# Phase 1.2+: Implement service methods here.

from __future__ import annotations

import datetime
import uuid
from typing import Optional, Sequence

import structlog
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.emergency.exceptions import EmergencyNotFoundError
from app.modules.emergency.models import EmergencyRequest, EmergencyStatusEnum
from app.modules.emergency.repository import EmergencyRepository
from app.modules.emergency.schemas import EmergencyRequestCreateSchema

logger = structlog.get_logger(__name__)


class EmergencyService:
    """
    Business logic for emergency requests.
    Rule: Service layer contains ALL business logic.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = EmergencyRepository(db)

    async def create_request(
        self,
        data: EmergencyRequestCreateSchema,
        requested_by: Optional[uuid.UUID] = None,
    ) -> EmergencyRequest:
        now = datetime.datetime.now(datetime.timezone.utc)
        year = now.year

        # Generate human-readable sequence number: EMR-{year}-{seq:04d} with collision retry
        for attempt in range(5):
            count = await self.repository.get_count_for_year(year)
            seq = count + 1 + attempt
            request_number = f"EMR-{year}-{seq:04d}"

            emergency_request = EmergencyRequest(
                id=uuid.uuid4(),
                request_number=request_number,
                requested_by=requested_by,
                patient_name=data.patient_name,
                patient_age=data.patient_age,
                blood_type=data.blood_type,
                units_required=data.units_required,
                units_fulfilled=0,
                urgency_level=data.urgency_level,
                hospital_name=data.hospital_name,
                hospital_id=data.hospital_id,
                facility_address=data.facility_address,
                city=data.city,
                latitude=data.latitude,
                longitude=data.longitude,
                status=EmergencyStatusEnum.PENDING.value,
                ai_assisted=True,
                notes=data.notes,
            )

            try:
                created = await self.repository.create(emergency_request)
                await self.db.commit()
                await self.db.refresh(created)
                logger.info(
                    "emergency_request_created",
                    request_id=str(created.id),
                    request_number=created.request_number,
                    blood_type=created.blood_type,
                    units_required=created.units_required,
                    urgency=created.urgency_level,
                    city=created.city,
                )
                return created
            except IntegrityError as exc:
                await self.db.rollback()
                if "request_number" in str(exc) and attempt < 4:
                    logger.warning(
                        "request_number_collision_retrying",
                        attempt=attempt,
                        candidate=request_number,
                    )
                    continue
                raise

        return created

    async def get_request(self, identifier: str) -> EmergencyRequest:
        req: Optional[EmergencyRequest] = None

        # Check if identifier is a valid UUID
        try:
            req_uuid = uuid.UUID(identifier)
            req = await self.repository.get_by_id(req_uuid)
        except ValueError:
            # Otherwise search by request_number (e.g. EMR-2026-0001)
            req = await self.repository.get_by_request_number(identifier.upper())

        if not req:
            logger.warning("emergency_request_not_found", identifier=identifier)
            raise EmergencyNotFoundError(identifier)

        return req

    async def list_requests(
        self,
        status: Optional[str] = None,
        blood_type: Optional[str] = None,
        city: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[Sequence[EmergencyRequest], int]:
        return await self.repository.list_requests(
            status=status,
            blood_type=blood_type,
            city=city,
            limit=limit,
            offset=offset,
        )

    async def update_status(
        self,
        identifier: str,
        new_status: str,
        cancellation_reason: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> EmergencyRequest:
        req = await self.get_request(identifier)
        clean_status = new_status.strip().upper()
        req.status = clean_status
        now = datetime.datetime.now(datetime.timezone.utc)

        if clean_status == EmergencyStatusEnum.CANCELLED.value:
            req.cancelled_at = now
            if cancellation_reason:
                req.cancellation_reason = cancellation_reason
        elif clean_status == EmergencyStatusEnum.FULFILLED.value:
            req.fulfilled_at = now
            req.units_fulfilled = req.units_required

        if notes:
            req.notes = notes

        await self.db.commit()
        await self.db.refresh(req)
        logger.info("emergency_request_status_updated", request_id=str(req.id), status=clean_status)
        return req
