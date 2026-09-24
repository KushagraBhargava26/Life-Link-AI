# backend/app/modules/emergency/gps_router.py
# LifeLink AI — Phase 1.8: Live GPS Telemetry Endpoints

from __future__ import annotations

import datetime
import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.modules.emergency.models import EmergencyRequest
from app.modules.emergency.gps_models import VehicleLocation

gps_router = APIRouter()


class LocationUpdateSchema(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    heading: Optional[float] = Field(None, ge=0.0, le=360.0)
    speed_kmh: Optional[float] = Field(None, ge=0.0)
    status_note: Optional[str] = Field(None, max_length=200)


class LocationResponseSchema(BaseModel):
    id: uuid.UUID
    request_id: uuid.UUID
    latitude: float
    longitude: float
    heading: Optional[float] = None
    speed_kmh: Optional[float] = None
    status_note: Optional[str] = None
    recorded_at: datetime.datetime

    class Config:
        from_attributes = True


async def _get_emergency_request(request_id: str, db: AsyncSession) -> EmergencyRequest:
    try:
        uid = uuid.UUID(request_id)
        result = await db.execute(
            select(EmergencyRequest).where(
                EmergencyRequest.id == uid,
                EmergencyRequest.deleted_at.is_(None),
            )
        )
    except ValueError:
        result = await db.execute(
            select(EmergencyRequest).where(
                EmergencyRequest.request_number == request_id.upper(),
                EmergencyRequest.deleted_at.is_(None),
            )
        )
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail=f"Emergency request not found.")
    return req


def _success(data: Any, message: str = "OK") -> dict:
    return {
        "success": True,
        "data": data,
        "message": message,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


@gps_router.post(
    "/{request_id}/location",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="[Phase 1.8] Update Vehicle GPS Location",
    tags=["GPS Telemetry"],
)
async def update_vehicle_location(
    request_id: str,
    payload: LocationUpdateSchema,
    db: AsyncSession = Depends(get_db),
) -> dict:
    req = await _get_emergency_request(request_id, db)
    location = VehicleLocation(
        id=uuid.uuid4(),
        request_id=req.id,
        latitude=float(payload.latitude),
        longitude=float(payload.longitude),
        heading=float(payload.heading) if payload.heading is not None else None,
        speed_kmh=float(payload.speed_kmh) if payload.speed_kmh is not None else None,
        status_note=payload.status_note,
        recorded_at=datetime.datetime.now(datetime.timezone.utc),
    )
    db.add(location)
    await db.commit()
    await db.refresh(location)
    resp = LocationResponseSchema.model_validate(location).model_dump(mode="json")
    return _success(data=resp, message="GPS location recorded.")


@gps_router.get(
    "/{request_id}/location",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="[Phase 1.8] Get Latest Vehicle GPS Location",
    tags=["GPS Telemetry"],
)
async def get_latest_location(
    request_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    req = await _get_emergency_request(request_id, db)
    result = await db.execute(
        select(VehicleLocation)
        .where(VehicleLocation.request_id == req.id)
        .order_by(desc(VehicleLocation.recorded_at))
        .limit(1)
    )
    location = result.scalar_one_or_none()
    if not location:
        return _success(data=None, message="No GPS data available yet.")
    resp = LocationResponseSchema.model_validate(location).model_dump(mode="json")
    return _success(data=resp)


@gps_router.get(
    "/{request_id}/location/history",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="[Phase 1.8] Get Vehicle GPS Track History",
    tags=["GPS Telemetry"],
)
async def get_location_history(
    request_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    req = await _get_emergency_request(request_id, db)
    result = await db.execute(
        select(VehicleLocation)
        .where(VehicleLocation.request_id == req.id)
        .order_by(VehicleLocation.recorded_at)
        .limit(200)
    )
    locations = result.scalars().all()
    resp = [LocationResponseSchema.model_validate(loc).model_dump(mode="json") for loc in locations]
    return _success(data=resp, message=f"{len(resp)} GPS points retrieved.")
