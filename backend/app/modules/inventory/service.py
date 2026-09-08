# backend/app/modules/inventory/service.py
# LifeLink AI — Blood Inventory Module Business Logic Service
# Architecture Reference: ARCHITECTURE.md Section 24, ADR-001; API.md Section 10

from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Any, Optional

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.medical import VALID_BLOOD_TYPES, get_compatible_donor_types
from app.modules.emergency.models import EmergencyRequest
from app.modules.emergency.repository import EmergencyRepository
from app.modules.inventory.exceptions import (
    InsufficientStockError,
    InvalidInventoryOperationError,
    InventoryNotFoundError,
)
from app.modules.inventory.models import BloodInventory, FacilityTypeEnum, InventoryChangeEnum, InventoryHistory
from app.modules.inventory.repository import InventoryRepository
from app.modules.inventory.schemas import (
    BloodBankEmergencyRespondRequestSchema,
    BloodInventoryBatchUpdateSchema,
    BloodInventoryUpdateSchema,
)

logger = structlog.get_logger(__name__)


class InventoryService:
    """Service handling business logic for blood inventory and compatibility availability."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = InventoryRepository(db)

    async def get_facility_inventory(
        self, facility_type: str, facility_id: uuid.UUID
    ) -> dict[str, Any]:
        """
        Get all 8 blood type inventory items for a facility.
        If a blood type has no record in the database yet, synthesizes a truthful 0-unit record.
        """
        rows = await self.repository.get_facility_inventory(facility_type, facility_id)
        row_map = {r.blood_type: r for r in rows}

        today = date.today()
        items = []
        total_available = 0
        total_reserved = 0
        expiring_soon_count = 0
        depleted_groups_count = 0
        stock_by_blood_type: dict[str, int] = {}

        for b_type in sorted(VALID_BLOOD_TYPES):
            row = row_map.get(b_type)
            if row:
                is_expired = bool(row.expiry_date and row.expiry_date < today)
                # Expired inventory must NEVER count toward available stock
                effective_units = 0 if is_expired else row.units_available
                net_available = max(0, effective_units - row.units_reserved)
                is_low_stock = bool(net_available <= row.minimum_threshold)

                # Expiring soon: within 7 days
                is_expiring_soon = bool(
                    row.expiry_date and not is_expired and (row.expiry_date - today).days <= 7
                )
                if is_expiring_soon and effective_units > 0:
                    expiring_soon_count += 1

                total_available += effective_units
                total_reserved += row.units_reserved
                if net_available <= row.minimum_threshold:
                    depleted_groups_count += 1
                stock_by_blood_type[b_type] = net_available

                items.append({
                    "id": row.id,
                    "facility_type": row.facility_type,
                    "facility_id": row.facility_id,
                    "blood_type": row.blood_type,
                    "component": row.component,
                    "units_available": row.units_available,
                    "units_reserved": row.units_reserved,
                    "net_available": net_available,
                    "minimum_threshold": row.minimum_threshold,
                    "last_restocked_at": row.last_restocked_at,
                    "expiry_date": row.expiry_date,
                    "is_expired": is_expired,
                    "is_low_stock": is_low_stock,
                    "created_at": row.created_at,
                    "updated_at": row.updated_at,
                })
            else:
                # Truthful zero state
                depleted_groups_count += 1
                stock_by_blood_type[b_type] = 0
                items.append({
                    "id": uuid.uuid4(),
                    "facility_type": facility_type,
                    "facility_id": facility_id,
                    "blood_type": b_type,
                    "component": "WHOLE_BLOOD",
                    "units_available": 0,
                    "units_reserved": 0,
                    "net_available": 0,
                    "minimum_threshold": 5,
                    "last_restocked_at": None,
                    "expiry_date": None,
                    "is_expired": False,
                    "is_low_stock": True,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                })

        summary = {
            "total_available": total_available,
            "total_reserved": total_reserved,
            "expiring_soon_count": expiring_soon_count,
            "depleted_groups_count": depleted_groups_count,
            "stock_by_blood_type": stock_by_blood_type,
        }

        return {
            "items": items,
            "summary": summary,
        }

    async def update_stock(
        self,
        facility_type: str,
        facility_id: uuid.UUID,
        blood_type: str,
        data: BloodInventoryUpdateSchema,
        user_id: uuid.UUID,
    ) -> dict[str, Any]:
        """Update inventory stock for a single blood type."""
        b_type = blood_type.strip().upper()
        if b_type not in VALID_BLOOD_TYPES:
            raise InvalidInventoryOperationError(f"Invalid blood type '{blood_type}'")

        if data.units_available < 0:
            raise InvalidInventoryOperationError("Units available cannot be negative")

        item, before, after = await self.repository.upsert_stock(
            facility_type=facility_type,
            facility_id=facility_id,
            blood_type=b_type,
            units_available=data.units_available,
            minimum_threshold=data.minimum_threshold,
            expiry_date=data.expiry_date,
            component=data.component,
            changed_by=user_id,
            change_type=InventoryChangeEnum.RESTOCK.value,
            reason=data.reason or f"Manual update to {data.units_available} units",
        )
        await self.db.commit()
        await self.db.refresh(item)

        today = date.today()
        is_expired = bool(item.expiry_date and item.expiry_date < today)
        effective = 0 if is_expired else item.units_available
        net = max(0, effective - item.units_reserved)

        return {
            "id": item.id,
            "facility_type": item.facility_type,
            "facility_id": item.facility_id,
            "blood_type": item.blood_type,
            "component": item.component,
            "units_available": item.units_available,
            "units_reserved": item.units_reserved,
            "net_available": net,
            "minimum_threshold": item.minimum_threshold,
            "last_restocked_at": item.last_restocked_at,
            "expiry_date": item.expiry_date,
            "is_expired": is_expired,
            "is_low_stock": net <= item.minimum_threshold,
            "created_at": item.created_at,
            "updated_at": item.updated_at,
        }

    async def batch_update_stock(
        self,
        facility_type: str,
        facility_id: uuid.UUID,
        data: BloodInventoryBatchUpdateSchema,
        user_id: uuid.UUID,
    ) -> list[dict[str, Any]]:
        """Batch update multiple blood types."""
        results = []
        for item_data in data.items:
            res = await self.update_stock(
                facility_type=facility_type,
                facility_id=facility_id,
                blood_type=item_data.blood_type,
                data=BloodInventoryUpdateSchema(
                    units_available=item_data.units_available,
                    minimum_threshold=item_data.minimum_threshold,
                    expiry_date=item_data.expiry_date,
                    component=item_data.component,
                    reason=item_data.reason or "Batch stock update",
                ),
                user_id=user_id,
            )
            results.append(res)
        return results

    async def check_demand_availability(
        self,
        facility_type: str,
        facility_id: uuid.UUID,
        request_id: uuid.UUID,
    ) -> dict[str, Any]:
        """
        Check deterministic compatibility and truthful availability for an emergency request.
        Zero patient PII returned.
        """
        emergency_repo = EmergencyRepository(self.db)
        emergency_req = await emergency_repo.get_by_id(request_id)
        if not emergency_req:
            raise InventoryNotFoundError(f"Emergency request with ID '{request_id}' not found")

        req_blood_type = emergency_req.blood_type
        component = "WHOLE_BLOOD"

        # 1. Deterministic compatible donor types
        compatible_types = list(get_compatible_donor_types(req_blood_type, component))

        # 2. Fetch inventory rows
        stock_rows = await self.repository.find_compatible_inventory(
            facility_type=facility_type,
            facility_id=facility_id,
            compatible_blood_types=compatible_types,
            component=component,
        )

        today = date.today()
        total_compatible_units = 0
        breakdown = []

        for row in stock_rows:
            # Exclude expired inventory!
            if row.expiry_date and row.expiry_date < today:
                continue

            net_units = max(0, row.units_available - row.units_reserved)
            if net_units > 0:
                total_compatible_units += net_units
                breakdown.append({
                    "blood_type": row.blood_type,
                    "units_available": net_units,
                    "is_exact_match": (row.blood_type == req_blood_type),
                })

        needed = emergency_req.units_required - emergency_req.units_fulfilled
        if total_compatible_units >= needed and needed > 0:
            status = "AVAILABLE"
            is_compatible_avail = True
        elif total_compatible_units > 0:
            status = "PARTIAL"
            is_compatible_avail = True
        else:
            status = "UNAVAILABLE"
            is_compatible_avail = False

        return {
            "request_id": emergency_req.id,
            "request_number": emergency_req.request_number,
            "blood_type": emergency_req.blood_type,
            "component": component,
            "units_required": emergency_req.units_required,
            "urgency_level": emergency_req.urgency_level,
            "hospital_name": emergency_req.hospital_name or "Emergency Center",
            "city": emergency_req.city,
            "status": emergency_req.status,
            "is_compatible_stock_available": is_compatible_avail,
            "availability_status": status,
            "total_compatible_units": total_compatible_units,
            "compatible_breakdown": breakdown,
        }

    async def respond_to_emergency_demand(
        self,
        blood_bank_id: uuid.UUID,
        request_id: uuid.UUID,
        data: BloodBankEmergencyRespondRequestSchema,
        user_id: uuid.UUID,
    ) -> dict[str, Any]:
        """
        Accept/Decline an emergency requisition with pessimistic row locking and real inventory reservation.
        """
        emergency_repo = EmergencyRepository(self.db)
        emergency_req = await emergency_repo.get_by_id(request_id)
        if not emergency_req:
            raise InventoryNotFoundError(f"Emergency request with ID '{request_id}' not found")

        blood_type = (data.blood_type or emergency_req.blood_type).strip().upper()
        units_to_commit = data.units_committed
        status = data.status.strip().upper()

        if status in ("ACCEPTED", "PARTIALLY_ACCEPTED") and units_to_commit > 0:
            # 1. Pessimistic lock on inventory row
            inventory_item = await self.repository.get_inventory_item(
                facility_type="BLOOD_BANK",
                facility_id=blood_bank_id,
                blood_type=blood_type,
                component="WHOLE_BLOOD",
                for_update=True,
            )
            if not inventory_item:
                raise InsufficientStockError(f"No inventory record found for blood type '{blood_type}'")

            today = date.today()
            if inventory_item.expiry_date and inventory_item.expiry_date < today:
                raise InsufficientStockError(f"Inventory for blood type '{blood_type}' is expired")

            net_available = inventory_item.units_available - inventory_item.units_reserved
            if net_available < units_to_commit:
                raise InsufficientStockError(
                    f"Insufficient stock for blood type '{blood_type}'. Available: {net_available}, Requested: {units_to_commit}"
                )

            # 2. Reserve stock: units_reserved += units_to_commit
            units_before = inventory_item.units_reserved
            inventory_item.units_reserved += units_to_commit
            now = datetime.now(timezone.utc)
            inventory_item.updated_at = now
            await self.db.flush()

            # 3. Log audit ledger
            history = InventoryHistory(
                id=uuid.uuid4(),
                inventory_id=inventory_item.id,
                changed_by=user_id,
                change_type=InventoryChangeEnum.EMERGENCY_USE.value,
                units_before=units_before,
                units_after=inventory_item.units_reserved,
                units_delta=units_to_commit,
                reason=f"Emergency reservation for request #{emergency_req.request_number}: {units_to_commit} units",
                emergency_request_id=emergency_req.id,
                created_at=now,
            )
            self.db.add(history)
            await self.db.flush()

            # 4. Update emergency request fulfilled units & status
            emergency_req.units_fulfilled = min(
                emergency_req.units_required, emergency_req.units_fulfilled + units_to_commit
            )
            if emergency_req.units_fulfilled >= emergency_req.units_required:
                emergency_req.status = "FULFILLED"
                emergency_req.fulfilled_at = now
            else:
                emergency_req.status = "IN_PROGRESS"
            await self.db.flush()

        # 5. Create / Update BloodBankEmergencyResponse
        resp = await self.repository.create_or_update_emergency_response(
            emergency_request_id=emergency_req.id,
            blood_bank_id=blood_bank_id,
            blood_type=blood_type,
            units_requested=emergency_req.units_required,
            units_committed=units_to_commit,
            status=status,
            message=data.message,
            responded_by=user_id,
        )

        await self.db.commit()
        await self.db.refresh(resp)
        logger.info(
            "blood_bank_emergency_response_recorded",
            blood_bank_id=str(blood_bank_id),
            request_id=str(request_id),
            units_committed=units_to_commit,
            status=status,
        )

        return {
            "id": resp.id,
            "emergency_request_id": resp.emergency_request_id,
            "blood_bank_id": resp.blood_bank_id,
            "blood_type": resp.blood_type,
            "units_requested": resp.units_requested,
            "units_committed": resp.units_committed,
            "status": resp.status,
            "message": resp.message,
            "responded_by": resp.responded_by,
            "created_at": resp.created_at,
            "updated_at": resp.updated_at,
        }
