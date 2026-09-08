# backend/app/modules/inventory/repository.py
# LifeLink AI — Blood Inventory Module Database Repository
# Architecture Reference: ARCHITECTURE.md Section 24, ADR-001; DATABASE.md Section 9

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from typing import Optional

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.models import (
    BloodBankEmergencyResponse,
    BloodInventory,
    InventoryChangeEnum,
    InventoryHistory,
)

logger = structlog.get_logger(__name__)


class InventoryRepository:
    """Async repository for BloodInventory and InventoryHistory entities."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_facility_inventory(
        self, facility_type: str, facility_id: uuid.UUID
    ) -> list[BloodInventory]:
        """Fetch all active blood inventory records for a facility."""
        stmt = (
            select(BloodInventory)
            .where(
                BloodInventory.facility_type == facility_type,
                BloodInventory.facility_id == facility_id,
                BloodInventory.deleted_at.is_(None),
            )
            .order_by(BloodInventory.blood_type.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_inventory_item(
        self,
        facility_type: str,
        facility_id: uuid.UUID,
        blood_type: str,
        component: str = "WHOLE_BLOOD",
        for_update: bool = False,
    ) -> Optional[BloodInventory]:
        """Fetch a specific blood inventory item, optionally with row-level lock (ADR-001)."""
        stmt = select(BloodInventory).where(
            BloodInventory.facility_type == facility_type,
            BloodInventory.facility_id == facility_id,
            BloodInventory.blood_type == blood_type,
            BloodInventory.component == component,
            BloodInventory.deleted_at.is_(None),
        )
        if for_update:
            stmt = stmt.with_for_update()

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_stock(
        self,
        facility_type: str,
        facility_id: uuid.UUID,
        blood_type: str,
        units_available: int,
        minimum_threshold: int = 5,
        expiry_date: Optional[date] = None,
        component: str = "WHOLE_BLOOD",
        changed_by: Optional[uuid.UUID] = None,
        change_type: str = InventoryChangeEnum.RESTOCK.value,
        reason: Optional[str] = None,
    ) -> tuple[BloodInventory, int, int]:
        """
        Upsert a blood inventory record with pessimistic row locking and record audit history.
        Returns (inventory_entity, units_before, units_after).
        """
        existing = await self.get_inventory_item(
            facility_type=facility_type,
            facility_id=facility_id,
            blood_type=blood_type,
            component=component,
            for_update=True,
        )

        now = datetime.now(timezone.utc)

        if existing:
            units_before = existing.units_available
            units_after = units_available
            existing.units_available = units_available
            existing.minimum_threshold = minimum_threshold
            existing.expiry_date = expiry_date
            existing.last_restocked_at = now
            existing.updated_at = now
            item = existing
        else:
            units_before = 0
            units_after = units_available
            item = BloodInventory(
                id=uuid.uuid4(),
                facility_type=facility_type,
                facility_id=facility_id,
                blood_type=blood_type,
                component=component,
                units_available=units_available,
                units_reserved=0,
                minimum_threshold=minimum_threshold,
                expiry_date=expiry_date,
                last_restocked_at=now,
                created_at=now,
                updated_at=now,
            )
            self.db.add(item)

        await self.db.flush()
        await self.db.refresh(item)

        # Audit ledger
        if changed_by:
            delta = units_after - units_before
            history = InventoryHistory(
                id=uuid.uuid4(),
                inventory_id=item.id,
                changed_by=changed_by,
                change_type=change_type,
                units_before=units_before,
                units_after=units_after,
                units_delta=delta,
                reason=reason or f"Stock updated to {units_after} units",
                created_at=now,
            )
            self.db.add(history)
            await self.db.flush()

        return item, units_before, units_after

    async def find_compatible_inventory(
        self,
        facility_type: str,
        facility_id: uuid.UUID,
        compatible_blood_types: list[str],
        component: str = "WHOLE_BLOOD",
    ) -> list[BloodInventory]:
        """Find compatible inventory rows for a facility with available stock."""
        stmt = (
            select(BloodInventory)
            .where(
                BloodInventory.facility_type == facility_type,
                BloodInventory.facility_id == facility_id,
                BloodInventory.blood_type.in_(compatible_blood_types),
                BloodInventory.component == component,
                BloodInventory.deleted_at.is_(None),
            )
            .order_by(BloodInventory.blood_type.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_or_update_emergency_response(
        self,
        emergency_request_id: uuid.UUID,
        blood_bank_id: uuid.UUID,
        blood_type: str,
        units_requested: int,
        units_committed: int,
        status: str,
        message: Optional[str],
        responded_by: Optional[uuid.UUID],
    ) -> BloodBankEmergencyResponse:
        stmt = select(BloodBankEmergencyResponse).where(
            BloodBankEmergencyResponse.emergency_request_id == emergency_request_id,
            BloodBankEmergencyResponse.blood_bank_id == blood_bank_id,
        )
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()

        now = datetime.now(timezone.utc)
        if existing:
            existing.blood_type = blood_type
            existing.units_committed = units_committed
            existing.status = status
            existing.message = message
            existing.responded_by = responded_by
            existing.updated_at = now
            resp = existing
        else:
            resp = BloodBankEmergencyResponse(
                id=uuid.uuid4(),
                emergency_request_id=emergency_request_id,
                blood_bank_id=blood_bank_id,
                blood_type=blood_type,
                units_requested=units_requested,
                units_committed=units_committed,
                status=status,
                message=message,
                responded_by=responded_by,
                created_at=now,
                updated_at=now,
            )
            self.db.add(resp)

        await self.db.flush()
        await self.db.refresh(resp)
        return resp

    async def get_emergency_response(
        self, emergency_request_id: uuid.UUID, blood_bank_id: uuid.UUID
    ) -> Optional[BloodBankEmergencyResponse]:
        stmt = select(BloodBankEmergencyResponse).where(
            BloodBankEmergencyResponse.emergency_request_id == emergency_request_id,
            BloodBankEmergencyResponse.blood_bank_id == blood_bank_id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_emergency_responses_for_request(
        self, emergency_request_id: uuid.UUID
    ) -> list[BloodBankEmergencyResponse]:
        stmt = (
            select(BloodBankEmergencyResponse)
            .where(BloodBankEmergencyResponse.emergency_request_id == emergency_request_id)
            .order_by(BloodBankEmergencyResponse.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
