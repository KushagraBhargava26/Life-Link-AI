# backend/app/modules/blood_bank/service.py
# LifeLink AI — Blood Bank Module Business Logic Service
# Architecture Reference: ARCHITECTURE.md Section 27; API.md Section 9

from __future__ import annotations

import uuid
from typing import Any, Optional

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.blood_bank.exceptions import (
    BloodBankAlreadyExistsError,
    BloodBankNotFoundError,
    BloodBankPermissionDeniedError,
)
from app.modules.blood_bank.models import BloodBank
from app.modules.blood_bank.repository import BloodBankRepository
from app.modules.blood_bank.schemas import BloodBankCreateSchema, BloodBankUpdateSchema

logger = structlog.get_logger(__name__)


class BloodBankService:
    """Service handling business logic for blood banks and emergency demand visibility."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = BloodBankRepository(db)

    async def create_profile(
        self, data: BloodBankCreateSchema, user_id: uuid.UUID
    ) -> BloodBank:
        existing = await self.repository.get_by_user_id(user_id)
        if existing:
            raise BloodBankAlreadyExistsError(
                "You already have a blood bank facility associated with your account"
            )

        if data.license_number:
            conflict = await self.repository.get_by_license_number(data.license_number)
            if conflict:
                raise BloodBankAlreadyExistsError(
                    f"A blood bank with license number '{data.license_number}' already exists"
                )

        blood_bank = BloodBank(
            name=data.name,
            license_number=data.license_number,
            hospital_id=data.hospital_id,
            address_line=data.address_line,
            city=data.city,
            state=data.state,
            pincode=data.pincode,
            latitude=data.latitude,
            longitude=data.longitude,
            phone=data.phone,
            email=data.email,
            operating_hours=data.operating_hours,
            is_24_hours=data.is_24_hours,
            accepts_walk_in=data.accepts_walk_in,
            license_issue_date=data.license_issue_date,
            license_expiry_date=data.license_expiry_date,
            certificate_url=data.certificate_url,
            status=data.status or "ACTIVE",
            is_verified=bool(data.license_number or data.license_issue_date or data.certificate_url),
            is_active=True,
            manager_user_id=user_id,
            created_by=user_id,
        )
        created = await self.repository.create(blood_bank)
        await self.db.commit()
        await self.db.refresh(created)
        logger.info("blood_bank_created", blood_bank_id=str(created.id), user_id=str(user_id))
        return created

    async def get_my_blood_bank(self, user_id: uuid.UUID) -> BloodBank:
        bank = await self.repository.get_by_user_id(user_id)
        if not bank:
            raise BloodBankNotFoundError("No blood bank facility profile associated with your account")
        return bank

    async def update_my_blood_bank(
        self, data: BloodBankUpdateSchema, user_id: uuid.UUID
    ) -> BloodBank:
        bank = await self.get_my_blood_bank(user_id)

        update_data = data.model_dump(exclude_unset=True)
        if "license_number" in update_data and update_data["license_number"]:
            lic = update_data["license_number"]
            conflict = await self.repository.get_by_license_number(lic)
            if conflict and conflict.id != bank.id:
                raise BloodBankAlreadyExistsError(
                    f"License number '{lic}' is already registered to another blood bank"
                )

        for key, value in update_data.items():
            setattr(bank, key, value)

        updated = await self.repository.update(bank)
        await self.db.commit()
        await self.db.refresh(updated)
        logger.info("blood_bank_updated", blood_bank_id=str(updated.id), user_id=str(user_id))
        return updated

    async def get_blood_bank_by_id(self, blood_bank_id: uuid.UUID) -> BloodBank:
        bank = await self.repository.get_by_id(blood_bank_id)
        if not bank:
            raise BloodBankNotFoundError(f"Blood bank with ID '{blood_bank_id}' not found")
        return bank

    async def list_blood_banks(
        self,
        city: Optional[str] = None,
        is_24_hours: Optional[bool] = None,
        is_verified: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[BloodBank], int]:
        return await self.repository.list_blood_banks(
            city=city,
            is_24_hours=is_24_hours,
            is_verified=is_verified,
            limit=limit,
            offset=offset,
        )

    async def get_blood_bank_dashboard(self, user_id: uuid.UUID) -> dict[str, Any]:
        bank = await self.get_my_blood_bank(user_id)
        demand_requests, total_demand = await self.repository.get_emergency_demand_in_city(
            bank.city, limit=10, offset=0
        )

        demand_items = [
            {
                "id": str(r.id),
                "request_number": r.request_number,
                "blood_type": r.blood_type,
                "units_required": r.units_required,
                "units_fulfilled": r.units_fulfilled,
                "urgency_level": r.urgency_level,
                "hospital_name": r.hospital_name or "Emergency Center",
                "city": r.city,
                "status": r.status,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in demand_requests
        ]

        return {
            "blood_bank": bank,
            "active_emergency_demand_count": total_demand,
            "is_operational": bank.is_active,
            "emergency_demand": demand_items,
        }

    async def get_emergency_demand(
        self, user_id: uuid.UUID, limit: int = 20, offset: int = 0
    ) -> tuple[list[dict[str, Any]], int]:
        bank = await self.get_my_blood_bank(user_id)
        demand_requests, total = await self.repository.get_emergency_demand_in_city(
            bank.city, limit=limit, offset=offset
        )
        items = [
            {
                "id": str(r.id),
                "request_number": r.request_number,
                "blood_type": r.blood_type,
                "units_required": r.units_required,
                "units_fulfilled": r.units_fulfilled,
                "urgency_level": r.urgency_level,
                "hospital_name": r.hospital_name or "Emergency Center",
                "city": r.city,
                "status": r.status,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in demand_requests
        ]
        return items, total
