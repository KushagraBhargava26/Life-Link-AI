# backend/app/modules/donor/service.py
# LifeLink AI — Donor Module Service Layer
# Architecture Reference: ARCHITECTURE.md Section 33 (Donor Workflow)

from __future__ import annotations

import datetime
import uuid
from typing import Optional

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.donor.exceptions import DonorNotFoundError
from app.modules.donor.models import Donor
from app.modules.donor.repository import DonorRepository
from app.modules.donor.schemas import (
    DonorAvailabilityToggleSchema,
    DonorCreateSchema,
    DonorResponseSchema,
    DonorUpdateSchema,
)

logger = structlog.get_logger(__name__)


class DonorService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = DonorRepository(db)

    def _to_response(self, donor: Donor) -> DonorResponseSchema:
        return DonorResponseSchema.model_validate(donor)

    async def get_profile(self, user_id: uuid.UUID) -> Donor:
        donor = await self.repository.get_by_user_id(user_id)
        if not donor:
            raise DonorNotFoundError(f"user {user_id}")
        return donor

    async def create_or_update_profile(
        self,
        user_id: uuid.UUID,
        data: DonorCreateSchema,
    ) -> Donor:
        existing = await self.repository.get_by_user_id(user_id)
        if existing:
            # Update existing donor record
            existing.blood_type = data.blood_type
            existing.city = data.city
            if data.state is not None:
                existing.state = data.state
            if data.pincode is not None:
                existing.pincode = data.pincode
            if data.weight_kg is not None:
                existing.weight_kg = data.weight_kg
            if data.date_of_birth is not None:
                existing.date_of_birth = data.date_of_birth
            if data.gender is not None:
                existing.gender = data.gender
            if data.address_line is not None:
                existing.address_line = data.address_line
            existing.is_available = data.is_available

            await self.repository.update(existing)
            await self.db.commit()
            await self.db.refresh(existing)
            logger.info("donor_profile_updated", user_id=str(user_id), blood_type=existing.blood_type)
            return existing

        # Create new donor record
        donor = Donor(
            id=uuid.uuid4(),
            user_id=user_id,
            blood_type=data.blood_type,
            city=data.city,
            state=data.state,
            pincode=data.pincode,
            weight_kg=data.weight_kg,
            date_of_birth=data.date_of_birth,
            gender=data.gender,
            address_line=data.address_line,
            is_available=data.is_available,
            is_eligible=True,
            total_donations=0,
        )
        created = await self.repository.create(donor)
        await self.db.commit()
        await self.db.refresh(created)
        logger.info("donor_profile_created", user_id=str(user_id), blood_type=created.blood_type)
        return created

    async def update_profile(
        self,
        user_id: uuid.UUID,
        data: DonorUpdateSchema,
    ) -> Donor:
        donor = await self.get_profile(user_id)

        if data.blood_type is not None:
            donor.blood_type = data.blood_type
        if data.city is not None:
            donor.city = data.city
        if data.state is not None:
            donor.state = data.state
        if data.pincode is not None:
            donor.pincode = data.pincode
        if data.weight_kg is not None:
            donor.weight_kg = data.weight_kg
        if data.date_of_birth is not None:
            donor.date_of_birth = data.date_of_birth
        if data.gender is not None:
            donor.gender = data.gender
        if data.address_line is not None:
            donor.address_line = data.address_line
        if data.is_available is not None:
            donor.is_available = data.is_available
        if data.last_donation_date is not None:
            donor.last_donation_date = data.last_donation_date
            # Check 56-day cooldown
            today = datetime.date.today()
            cooldown_days = (today - data.last_donation_date).days
            donor.is_eligible = cooldown_days >= 56

        await self.repository.update(donor)
        await self.db.commit()
        await self.db.refresh(donor)
        logger.info("donor_profile_patched", user_id=str(user_id))
        return donor

    async def toggle_availability(
        self,
        user_id: uuid.UUID,
        is_available: bool,
    ) -> Donor:
        donor = await self.get_profile(user_id)
        donor.is_available = is_available
        await self.repository.update(donor)
        await self.db.commit()
        await self.db.refresh(donor)
        logger.info("donor_availability_toggled", user_id=str(user_id), is_available=is_available)
        return donor

    async def get_dashboard_data(self, user_id: uuid.UUID) -> dict[str, Any]:
        from app.core.medical import is_compatible
        from app.modules.donor.schemas import (
            CompatibleEmergencyOpportunitySchema,
            DonorDashboardSchema,
            DonorResponseSchema,
        )
        from app.modules.emergency.models import EmergencyRequest, EmergencyStatusEnum
        from sqlalchemy import select

        donor = await self.repository.get_by_user_id(user_id)
        if not donor:
            return DonorDashboardSchema(
                profile=None,
                has_profile=False,
                is_available=False,
                is_eligible=False,
                next_eligible_date=None,
                days_until_eligible=0,
                total_donations=0,
                estimated_lives_saved=0,
                compatible_opportunities=[],
            ).model_dump(mode="json")

        today = datetime.date.today()
        next_eligible_date = None
        days_until_eligible = 0

        if donor.last_donation_date:
            next_eligible_date = donor.last_donation_date + datetime.timedelta(days=56)
            if next_eligible_date > today:
                days_until_eligible = (next_eligible_date - today).days
            else:
                days_until_eligible = 0

        # Query active emergency requests
        active_statuses = [
            EmergencyStatusEnum.PENDING.value,
            EmergencyStatusEnum.MATCHING.value,
            EmergencyStatusEnum.NOTIFIED.value,
            EmergencyStatusEnum.IN_PROGRESS.value,
        ]
        stmt = (
            select(EmergencyRequest)
            .where(
                EmergencyRequest.status.in_(active_statuses),
                EmergencyRequest.deleted_at == None,  # noqa: E711
            )
            .order_by(EmergencyRequest.created_at.desc())
            .limit(20)
        )
        res = await self.db.execute(stmt)
        requests = res.scalars().all()

        opportunities: list[CompatibleEmergencyOpportunitySchema] = []
        for req in requests:
            try:
                if is_compatible(donor.blood_type, req.blood_type):
                    opportunities.append(
                        CompatibleEmergencyOpportunitySchema(
                            id=req.id,
                            request_number=req.request_number,
                            blood_type=req.blood_type,
                            component="WHOLE_BLOOD",
                            units_requested=req.units_required,
                            urgency_level=req.urgency_level,
                            hospital_name=req.hospital_name,
                            city=req.city,
                            state="Active Request",
                            created_at=req.created_at,
                        )
                    )
            except Exception:
                continue

        profile_schema = DonorResponseSchema.model_validate(donor)

        return DonorDashboardSchema(
            profile=profile_schema,
            has_profile=True,
            is_available=donor.is_available,
            is_eligible=donor.is_eligible and days_until_eligible == 0,
            next_eligible_date=next_eligible_date,
            days_until_eligible=days_until_eligible,
            total_donations=donor.total_donations,
            estimated_lives_saved=donor.total_donations * 3,
            compatible_opportunities=opportunities[:10],
        ).model_dump(mode="json")

    async def get_opportunity_detail(
        self,
        user_id: uuid.UUID,
        request_id: uuid.UUID,
    ) -> dict[str, Any]:
        from app.core.exceptions import NotFoundError
        from app.core.medical import is_compatible
        from app.modules.donor.models import DonorEmergencyResponse
        from app.modules.donor.schemas import (
            DonorOpportunityDetailSchema,
            DonorOpportunityResponseSchema,
        )
        from app.modules.emergency.models import EmergencyRequest
        from sqlalchemy import select

        donor = await self.repository.get_by_user_id(user_id)
        if not donor:
            raise DonorNotFoundError(f"user {user_id}")

        req_stmt = select(EmergencyRequest).where(
            EmergencyRequest.id == request_id,
            EmergencyRequest.deleted_at == None,  # noqa: E711
        )
        req_res = await self.db.execute(req_stmt)
        req = req_res.scalar_one_or_none()
        if not req:
            raise NotFoundError(f"Emergency request {request_id} not found")

        is_comp = False
        try:
            is_comp = is_compatible(donor.blood_type, req.blood_type)
        except Exception:
            is_comp = False

        # Check existing donor response
        resp_stmt = select(DonorEmergencyResponse).where(
            DonorEmergencyResponse.emergency_request_id == req.id,
            DonorEmergencyResponse.donor_id == donor.id,
            DonorEmergencyResponse.deleted_at == None,  # noqa: E711
        )
        resp_res = await self.db.execute(resp_stmt)
        existing_resp = resp_res.scalar_one_or_none()

        donor_resp_schema = (
            DonorOpportunityResponseSchema.model_validate(existing_resp)
            if existing_resp
            else None
        )

        return DonorOpportunityDetailSchema(
            id=req.id,
            request_number=req.request_number,
            blood_type=req.blood_type,
            component="WHOLE_BLOOD",
            units_requested=req.units_required,
            units_fulfilled=req.units_fulfilled,
            urgency_level=req.urgency_level,
            hospital_name=req.hospital_name,
            facility_address=req.facility_address,
            city=req.city,
            status=req.status,
            created_at=req.created_at,
            is_compatible=is_comp,
            donor_blood_type=donor.blood_type,
            donor_response=donor_resp_schema,
        ).model_dump(mode="json")

    async def respond_to_opportunity(
        self,
        user_id: uuid.UUID,
        request_id: uuid.UUID,
        status: str,
        notes: Optional[str] = None,
    ) -> dict[str, Any]:
        from app.core.exceptions import NotFoundError, ValidationError
        from app.core.medical import is_compatible
        from app.modules.donor.models import DonorEmergencyResponse
        from app.modules.donor.schemas import DonorOpportunityResponseSchema
        from app.modules.emergency.models import EmergencyRequest, EmergencyStatusEnum
        from sqlalchemy import select

        donor = await self.repository.get_by_user_id(user_id)
        if not donor:
            raise DonorNotFoundError(f"user {user_id}")

        req_stmt = select(EmergencyRequest).where(
            EmergencyRequest.id == request_id,
            EmergencyRequest.deleted_at == None,  # noqa: E711
        )
        req_res = await self.db.execute(req_stmt)
        req = req_res.scalar_one_or_none()
        if not req:
            raise NotFoundError(f"Emergency request {request_id} not found")

        # Inactive request validation
        inactive_statuses = {
            EmergencyStatusEnum.CANCELLED.value,
            EmergencyStatusEnum.EXPIRED.value,
            EmergencyStatusEnum.FULFILLED.value,
        }
        if req.status in inactive_statuses:
            raise ValidationError(
                f"Emergency request {req.request_number} is already {req.status.lower()} and no longer accepting donor responses."
            )

        if status == "ACCEPTED":
            # Medical cooldown validation
            if donor.last_donation_date:
                today = datetime.date.today()
                days_since = (today - donor.last_donation_date).days
                if days_since < 56:
                    days_left = 56 - days_since
                    raise ValidationError(
                        f"Donor is currently in a 56-day cooldown period ({days_left} days remaining) and ineligible to donate."
                    )

            # Compatibility validation
            if not is_compatible(donor.blood_type, req.blood_type):
                raise ValidationError(
                    f"Donor blood type {donor.blood_type} is not compatible with required blood type {req.blood_type}."
                )

        now = datetime.datetime.now(datetime.timezone.utc)

        resp_stmt = select(DonorEmergencyResponse).where(
            DonorEmergencyResponse.emergency_request_id == req.id,
            DonorEmergencyResponse.donor_id == donor.id,
            DonorEmergencyResponse.deleted_at == None,  # noqa: E711
        )
        resp_res = await self.db.execute(resp_stmt)
        existing_resp = resp_res.scalar_one_or_none()

        if existing_resp:
            existing_resp.status = status
            if notes is not None:
                existing_resp.notes = notes
            existing_resp.responded_at = now
            await self.db.commit()
            await self.db.refresh(existing_resp)
            logger.info(
                "donor_response_updated",
                request_id=str(req.id),
                donor_id=str(donor.id),
                status=status,
            )
            return DonorOpportunityResponseSchema.model_validate(existing_resp).model_dump(
                mode="json"
            )

        new_resp = DonorEmergencyResponse(
            id=uuid.uuid4(),
            emergency_request_id=req.id,
            donor_id=donor.id,
            status=status,
            notes=notes,
            responded_at=now,
        )
        self.db.add(new_resp)
        await self.db.commit()
        await self.db.refresh(new_resp)
        logger.info(
            "donor_response_created",
            request_id=str(req.id),
            donor_id=str(donor.id),
            status=status,
        )
        return DonorOpportunityResponseSchema.model_validate(new_resp).model_dump(
            mode="json"
        )


