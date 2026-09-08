"""Matching service orchestrating deterministic filtering, distance, AI ranking & persistence."""

from __future__ import annotations
import math
import uuid
import time
from datetime import date, datetime
from typing import Optional, List, Dict, Any, Tuple

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.medical import get_compatible_donor_types
from app.modules.emergency.models import EmergencyRequest, EmergencyStatusEnum
from app.modules.donor.models import Donor, DonorEmergencyResponse
from app.modules.hospital.models import Hospital
from app.modules.blood_bank.models import BloodBank
from app.modules.inventory.models import BloodBankEmergencyResponse, BloodInventory
from app.modules.matching.models import (
    MatchRun,
    MatchCandidate,
    MatchRunStatusEnum,
    MatchCandidateTypeEnum,
    MatchCandidateStatusEnum,
)
from app.modules.matching.repository import MatchingRepository
from app.modules.matching.schemas import (
    MatchRunResponseSchema,
    MatchCandidateResponseSchema,
)
from app.modules.matching.exceptions import (
    MatchRunNotFoundError,
    CandidateNotFoundError,
    RequestNotEligibleForMatchingError,
)
from app.modules.ai_gateway.service import AiGatewayService


def calculate_haversine_distance(
    lat1: Optional[float],
    lon1: Optional[float],
    lat2: Optional[float],
    lon2: Optional[float],
) -> Optional[float]:
    """Calculates deterministic Haversine distance in km between two coordinate pairs."""
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return None

    # Earth radius in kilometers
    R = 6371.0

    phi1 = math.radians(float(lat1))
    phi2 = math.radians(float(lat2))
    delta_phi = math.radians(float(lat2) - float(lat1))
    delta_lambda = math.radians(float(lon2) - float(lon1))

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    distance = R * c
    return round(distance, 2)


class MatchingService:
    """Orchestrates candidate discovery, deterministic filtering, AI ranking & audit logging."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = MatchingRepository(db)
        self.ai_gateway = AiGatewayService()

    async def execute_matching(
        self,
        emergency_request_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
        search_radius_km: float = 50.0,
    ) -> MatchRunResponseSchema:
        """Executes full matching pipeline for an emergency request."""
        start_time = time.time()

        # 1. Load Emergency Request
        stmt = select(EmergencyRequest).where(
            EmergencyRequest.id == emergency_request_id,
            EmergencyRequest.deleted_at.is_(None),
        )
        res = await self.db.execute(stmt)
        req: Optional[EmergencyRequest] = res.scalar_one_or_none()
        if not req:
            raise MatchRunNotFoundError("Emergency request not found")

        # 2. Origin Coordinates
        origin_lat = float(req.latitude) if req.latitude is not None else None
        origin_lon = float(req.longitude) if req.longitude is not None else None

        # Fallback to hospital coordinates if request coords missing
        if (origin_lat is None or origin_lon is None) and req.hospital_id:
            hosp_stmt = select(Hospital).where(Hospital.id == req.hospital_id)
            hosp_res = await self.db.execute(hosp_stmt)
            hosp = hosp_res.scalar_one_or_none()
            if hosp and hosp.latitude and hosp.longitude:
                origin_lat = float(hosp.latitude)
                origin_lon = float(hosp.longitude)

        # 3. Deterministic Compatibility Gate (Critical Invariant 1 & 2)
        compatible_types = get_compatible_donor_types(req.blood_type, "WHOLE_BLOOD")

        # 4. Discover Blood Bank Candidates with Compatible Inventory
        blood_bank_candidates = await self._discover_blood_banks(
            req=req,
            compatible_types=compatible_types,
            origin_lat=origin_lat,
            origin_lon=origin_lon,
            search_radius_km=search_radius_km,
        )

        # 5. Discover Eligible & Available Donors
        donor_candidates, donor_features = await self._discover_donors(
            req=req,
            compatible_types=compatible_types,
            origin_lat=origin_lat,
            origin_lon=origin_lon,
            search_radius_km=search_radius_km,
        )

        total_evaluated = len(blood_bank_candidates) + len(donor_candidates)

        # 6. AI Ranking Layer (or Deterministic Fallback if AI unavailable)
        ai_resp = await self.ai_gateway.rank_donor_candidates(
            request_id=str(req.id),
            blood_type_required=req.blood_type,
            urgency_level=req.urgency_level,
            search_radius_km=search_radius_km,
            candidates=donor_features,
        )

        model_version = "donor-response-v1"
        algorithm = "calibrated_logistic_regression_hybrid"

        if ai_resp and "candidates" in ai_resp and ai_resp["candidates"]:
            # AI Succeeded
            ranked_donors_map = {c["donor_id"]: c for c in ai_resp["candidates"]}
            scored_donors: List[Dict[str, Any]] = []
            for d in donor_candidates:
                d_id = str(d["donor"].id)
                ai_c = ranked_donors_map.get(d_id)
                if ai_c:
                    scored_donors.append({
                        "donor": d["donor"],
                        "total_score": ai_c["total_score"],
                        "compatibility_score": ai_c["compatibility_score"],
                        "proximity_score": ai_c["proximity_score"],
                        "availability_score": ai_c["availability_score"],
                        "ai_score": ai_c.get("propensity_score"),
                        "distance_km": ai_c.get("distance_km"),
                        "explanation": ai_c.get("explanation", []),
                    })
            scored_donors.sort(key=lambda x: x["total_score"], reverse=True)
        else:
            # Deterministic Fallback (Critical Invariant 3)
            model_version = "deterministic-fallback"
            algorithm = "deterministic_rule_engine"
            scored_donors = []
            for d in donor_candidates:
                donor = d["donor"]
                dist = d["distance_km"]
                compat = 1.0 if donor.blood_type == req.blood_type else 0.8
                prox = max(0.0, 1.0 - (dist / search_radius_km)) if dist is not None else 0.50
                avail = 1.0
                total = round((compat * 0.40) + (prox * 0.35) + (avail * 0.25), 4)

                exp = [
                    f"Compatible blood type ({donor.blood_type})",
                    "Active & available donor",
                    "AI ranking unavailable — showing deterministic operational ranking",
                ]
                if dist is not None:
                    exp.append(f"Located {dist:.1f} km away")
                else:
                    exp.append("Local municipality match")

                scored_donors.append({
                    "donor": donor,
                    "total_score": total,
                    "compatibility_score": compat,
                    "proximity_score": prox,
                    "availability_score": avail,
                    "ai_score": None,
                    "distance_km": dist,
                    "explanation": exp,
                })
            scored_donors.sort(key=lambda x: x["total_score"], reverse=True)

        # 7. Sort Blood Banks
        blood_bank_candidates.sort(key=lambda x: x["total_score"], reverse=True)

        duration_ms = round((time.time() - start_time) * 1000.0, 2)
        next_run_num = await self.repo.get_next_run_number(req.id)

        # 8. Create MatchRun record
        status = MatchRunStatusEnum.COMPLETED if (blood_bank_candidates or scored_donors) else MatchRunStatusEnum.NO_CANDIDATES
        run = MatchRun(
            emergency_request_id=req.id,
            run_number=next_run_num,
            status=status,
            model_version=model_version,
            algorithm=algorithm,
            search_radius_km=search_radius_km,
            candidates_evaluated=total_evaluated,
            donors_matched=len(scored_donors),
            blood_banks_matched=len(blood_bank_candidates),
            execution_duration_ms=duration_ms,
            executed_by=user_id,
        )
        await self.repo.create_match_run(run)

        # 9. Create Candidate Entities
        db_candidates: List[MatchCandidate] = []
        overall_rank = 1

        # Blood banks
        bb_response_items: List[MatchCandidateResponseSchema] = []
        for bb_item in blood_bank_candidates:
            bb = bb_item["blood_bank"]
            cand_id = uuid.uuid4()
            cand = MatchCandidate(
                id=cand_id,
                match_run_id=run.id,
                emergency_request_id=req.id,
                candidate_type=MatchCandidateTypeEnum.BLOOD_BANK,
                blood_bank_id=bb.id,
                rank=overall_rank,
                total_score=bb_item["total_score"],
                compatibility_score=bb_item["compatibility_score"],
                proximity_score=bb_item["proximity_score"],
                availability_score=bb_item["availability_score"],
                ai_score=None,
                distance_km=bb_item["distance_km"],
                units_available=bb_item["units_available"],
                status=MatchCandidateStatusEnum.PROPOSED,
                explanation=bb_item["explanation"],
            )
            db_candidates.append(cand)

            # Check blood bank response status
            bb_resp_stmt = select(BloodBankEmergencyResponse).where(
                BloodBankEmergencyResponse.emergency_request_id == req.id,
                BloodBankEmergencyResponse.blood_bank_id == bb.id,
            )
            bb_resp_res = await self.db.execute(bb_resp_stmt)
            bb_resp_obj = bb_resp_res.scalar_one_or_none()
            bb_resp_status = bb_resp_obj.status if bb_resp_obj else None
            bb_units_committed = bb_resp_obj.units_committed if bb_resp_obj else None

            loc_disp = f"{bb_item['distance_km']:.1f} km away" if bb_item['distance_km'] is not None else f"{bb.city} (coords pending)"
            bb_response_items.append(
                MatchCandidateResponseSchema(
                    id=cand_id,
                    rank=overall_rank,
                    candidate_type="BLOOD_BANK",
                    candidate_id=str(bb.id),
                    name=bb.name,
                    blood_type=req.blood_type,
                    compatibility_score=bb_item["compatibility_score"],
                    proximity_score=bb_item["proximity_score"],
                    availability_score=bb_item["availability_score"],
                    ai_score=None,
                    total_score=bb_item["total_score"],
                    distance_km=bb_item["distance_km"],
                    units_available=bb_item["units_available"],
                    status="PROPOSED",
                    blood_bank_response_status=bb_resp_status,
                    units_committed=bb_units_committed,
                    explanation=bb_item["explanation"],
                    location_display=loc_disp,
                    is_compatible=True,
                )
            )
            overall_rank += 1

        # Donors
        donor_response_items: List[MatchCandidateResponseSchema] = []
        for d_item in scored_donors:
            donor = d_item["donor"]
            cand_id = uuid.uuid4()
            cand = MatchCandidate(
                id=cand_id,
                match_run_id=run.id,
                emergency_request_id=req.id,
                candidate_type=MatchCandidateTypeEnum.DONOR,
                donor_id=donor.id,
                rank=overall_rank,
                total_score=d_item["total_score"],
                compatibility_score=d_item["compatibility_score"],
                proximity_score=d_item["proximity_score"],
                availability_score=d_item["availability_score"],
                ai_score=d_item.get("ai_score"),
                distance_km=d_item.get("distance_km"),
                units_available=1,
                status=MatchCandidateStatusEnum.PROPOSED,
                explanation=d_item["explanation"],
            )
            db_candidates.append(cand)

            # Check donor response status
            donor_resp_stmt = select(DonorEmergencyResponse).where(
                DonorEmergencyResponse.emergency_request_id == req.id,
                DonorEmergencyResponse.donor_id == donor.id,
                DonorEmergencyResponse.deleted_at.is_(None),
            )
            donor_resp_res = await self.db.execute(donor_resp_stmt)
            d_resp_obj = donor_resp_res.scalar_one_or_none()
            donor_resp_status = d_resp_obj.status if d_resp_obj else "PENDING"

            short_hash = str(donor.id).split("-")[0].upper()
            loc_disp = f"{d_item['distance_km']:.1f} km away" if d_item['distance_km'] is not None else f"{donor.city} (coords pending)"
            donor_response_items.append(
                MatchCandidateResponseSchema(
                    id=cand_id,
                    rank=overall_rank,
                    candidate_type="DONOR",
                    candidate_id=str(donor.id),
                    name=f"Donor #{short_hash}",
                    blood_type=donor.blood_type,
                    compatibility_score=d_item["compatibility_score"],
                    proximity_score=d_item["proximity_score"],
                    availability_score=d_item["availability_score"],
                    ai_score=d_item.get("ai_score"),
                    total_score=d_item["total_score"],
                    distance_km=d_item.get("distance_km"),
                    units_available=1,
                    status="PROPOSED",
                    donor_response_status=donor_resp_status,
                    explanation=d_item["explanation"],
                    location_display=loc_disp,
                    is_compatible=True,
                )
            )

            overall_rank += 1

        if db_candidates:
            await self.repo.create_candidates(db_candidates)

        # Update emergency request status if appropriate
        if req.status == EmergencyStatusEnum.PENDING.value and (blood_bank_candidates or scored_donors):
            req.status = EmergencyStatusEnum.MATCHING.value

        await self.db.commit()

        return MatchRunResponseSchema(
            id=run.id,
            emergency_request_id=req.id,
            run_number=run.run_number,
            status=run.status.value,
            model_version=run.model_version,
            algorithm=run.algorithm,
            search_radius_km=run.search_radius_km,
            candidates_evaluated=run.candidates_evaluated,
            donors_matched=run.donors_matched,
            blood_banks_matched=run.blood_banks_matched,
            execution_duration_ms=run.execution_duration_ms,
            created_at=run.created_at,
            blood_banks=bb_response_items,
            donors=donor_response_items,
        )

    async def _discover_blood_banks(
        self,
        req: EmergencyRequest,
        compatible_types: frozenset[str],
        origin_lat: Optional[float],
        origin_lon: Optional[float],
        search_radius_km: float,
    ) -> List[Dict[str, Any]]:
        """Queries active blood banks having non-expired compatible stock."""
        today = date.today()

        # Query verified active blood banks
        bb_stmt = select(BloodBank).where(
            BloodBank.deleted_at.is_(None),
            BloodBank.is_active.is_(True),
            BloodBank.is_verified.is_(True),
        )
        bb_res = await self.db.execute(bb_stmt)
        blood_banks = bb_res.scalars().all()

        results: List[Dict[str, Any]] = []

        for bb in blood_banks:
            # Query compatible non-expired inventory for this facility
            inv_stmt = select(BloodInventory).where(
                BloodInventory.facility_type == "BLOOD_BANK",
                BloodInventory.facility_id == bb.id,
                BloodInventory.blood_type.in_(list(compatible_types)),
                BloodInventory.deleted_at.is_(None),
                or_(BloodInventory.expiry_date.is_(None), BloodInventory.expiry_date >= today),
            )
            inv_res = await self.db.execute(inv_stmt)
            inv_rows = inv_res.scalars().all()

            total_units = 0
            has_exact = False
            for inv in inv_rows:
                net = max(0, inv.units_available - inv.units_reserved)
                total_units += net
                if inv.blood_type == req.blood_type:
                    has_exact = True

            if total_units <= 0:
                continue

            # Calculate distance
            bb_lat = float(bb.latitude) if bb.latitude is not None else None
            bb_lon = float(bb.longitude) if bb.longitude is not None else None
            dist = calculate_haversine_distance(origin_lat, origin_lon, bb_lat, bb_lon)

            # Spatial filter: if distance is known, discard if > search_radius
            if dist is not None and dist > search_radius_km:
                continue
            # If coordinates missing, ensure city match
            if dist is None and bb.city.strip().lower() != req.city.strip().lower():
                continue

            # Scoring
            compat_score = 1.0 if has_exact else 0.85
            stock_score = min(1.0, float(total_units) / float(req.units_required))
            prox_score = max(0.0, 1.0 - (dist / search_radius_km)) if dist is not None else 0.50
            avail_score = 1.0

            total_score = round(
                (compat_score * 0.40) + (stock_score * 0.35) + (prox_score * 0.25),
                4,
            )

            exp = [
                f"Verified cold storage: {total_units} compatible units on hand",
                "Exact ABO/Rh match available" if has_exact else "Universal compatible stock available",
                "24/7 operating facility" if bb.is_24_hours else "Standard operating hours",
            ]
            if dist is not None:
                exp.append(f"Located {dist:.1f} km from facility")
            else:
                exp.append(f"Local {bb.city} facility")

            results.append({
                "blood_bank": bb,
                "units_available": total_units,
                "distance_km": dist,
                "total_score": total_score,
                "compatibility_score": compat_score,
                "proximity_score": prox_score,
                "availability_score": avail_score,
                "explanation": exp,
            })

        return results

    async def _discover_donors(
        self,
        req: EmergencyRequest,
        compatible_types: frozenset[str],
        origin_lat: Optional[float],
        origin_lon: Optional[float],
        search_radius_km: float,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Queries eligible, available, compatible donors within radius."""
        today = date.today()

        donor_stmt = select(Donor).where(
            Donor.deleted_at.is_(None),
            Donor.is_available.is_(True),
            Donor.is_eligible.is_(True),
            Donor.blood_type.in_(list(compatible_types)),
        )
        res = await self.db.execute(donor_stmt)
        all_donors = res.scalars().all()

        candidate_list: List[Dict[str, Any]] = []
        feature_vectors: List[Dict[str, Any]] = []

        for donor in all_donors:
            # 56-day cooldown safeguard
            if donor.last_donation_date:
                days_since = (today - donor.last_donation_date).days
                if days_since < 56:
                    continue
                recency_months = round(float(days_since) / 30.4375, 1)
            else:
                recency_months = 12.0  # Cold-start baseline

            # Distance
            d_lat = float(donor.latitude) if donor.latitude is not None else None
            d_lon = float(donor.longitude) if donor.longitude is not None else None
            dist = calculate_haversine_distance(origin_lat, origin_lon, d_lat, d_lon)

            # Spatial filter
            if dist is not None and dist > search_radius_km:
                continue
            if dist is None and donor.city.strip().lower() != req.city.strip().lower():
                continue

            # Registration tenure
            if donor.created_at:
                created_dt = donor.created_at.date() if isinstance(donor.created_at, datetime) else donor.created_at
                tenure_months = round(float(max(1, (today - created_dt).days)) / 30.4375, 1)
            else:
                tenure_months = 12.0

            time_months = max(recency_months, tenure_months)
            compat_score = 1.0 if donor.blood_type == req.blood_type else 0.80

            candidate_list.append({
                "donor": donor,
                "distance_km": dist,
            })

            feature_vectors.append({
                "donor_id": str(donor.id),
                "blood_type": donor.blood_type,
                "compatibility_score": compat_score,
                "availability_score": 1.0,
                "recency_months": recency_months,
                "frequency_donations": int(donor.total_donations or 0),
                "time_months": time_months,
                "distance_km": dist,
            })

        return candidate_list, feature_vectors

    async def get_matches_for_request(
        self,
        emergency_request_id: uuid.UUID,
    ) -> Optional[MatchRunResponseSchema]:
        """Retrieves the latest match run for an emergency request."""
        run = await self.repo.get_latest_run_for_request(emergency_request_id)
        if not run:
            return None

        # Fetch emergency request to get requested blood type
        req_stmt = select(EmergencyRequest).where(EmergencyRequest.id == emergency_request_id)
        req_res = await self.db.execute(req_stmt)
        req = req_res.scalar_one_or_none()
        req_btype = req.blood_type if req else "Unknown"

        bb_items: List[MatchCandidateResponseSchema] = []
        donor_items: List[MatchCandidateResponseSchema] = []

        for cand in run.candidates:
            if cand.candidate_type == MatchCandidateTypeEnum.BLOOD_BANK:
                bb_name = "Blood Bank Facility"
                bb_resp_status = None
                bb_units_committed = None
                if cand.blood_bank_id:
                    b_stmt = select(BloodBank).where(BloodBank.id == cand.blood_bank_id)
                    b_res = await self.db.execute(b_stmt)
                    b_obj = b_res.scalar_one_or_none()
                    if b_obj:
                        bb_name = b_obj.name

                    # Check blood bank response status
                    bb_resp_stmt = select(BloodBankEmergencyResponse).where(
                        BloodBankEmergencyResponse.emergency_request_id == run.emergency_request_id,
                        BloodBankEmergencyResponse.blood_bank_id == cand.blood_bank_id,
                    )
                    bb_resp_res = await self.db.execute(bb_resp_stmt)
                    bb_resp_obj = bb_resp_res.scalar_one_or_none()
                    if bb_resp_obj:
                        bb_resp_status = bb_resp_obj.status
                        bb_units_committed = bb_resp_obj.units_committed

                loc = f"{cand.distance_km:.1f} km away" if cand.distance_km is not None else "Local facility"
                bb_items.append(
                    MatchCandidateResponseSchema(
                        id=cand.id,
                        rank=cand.rank,
                        candidate_type="BLOOD_BANK",
                        candidate_id=str(cand.blood_bank_id),
                        name=bb_name,
                        blood_type=req_btype,
                        compatibility_score=cand.compatibility_score,
                        proximity_score=cand.proximity_score,
                        availability_score=cand.availability_score,
                        ai_score=cand.ai_score,
                        total_score=cand.total_score,
                        distance_km=cand.distance_km,
                        units_available=cand.units_available,
                        status=cand.status.value,
                        blood_bank_response_status=bb_resp_status,
                        units_committed=bb_units_committed,
                        explanation=cand.explanation or [],
                        location_display=loc,
                        is_compatible=True,
                    )
                )
            else:
                d_id_str = str(cand.donor_id) if cand.donor_id else "UNKNOWN"
                short = d_id_str.split("-")[0].upper()
                d_btype = req_btype
                if cand.donor_id:
                    d_stmt = select(Donor).where(Donor.id == cand.donor_id)
                    d_res = await self.db.execute(d_stmt)
                    d_obj = d_res.scalar_one_or_none()
                    if d_obj:
                        d_btype = d_obj.blood_type

                loc = f"{cand.distance_km:.1f} km away" if cand.distance_km is not None else "Local donor"

                # Check donor response status
                donor_resp_status = "PENDING"
                if cand.donor_id:
                    donor_resp_stmt = select(DonorEmergencyResponse).where(
                        DonorEmergencyResponse.emergency_request_id == run.emergency_request_id,
                        DonorEmergencyResponse.donor_id == cand.donor_id,
                        DonorEmergencyResponse.deleted_at.is_(None),
                    )
                    donor_resp_res = await self.db.execute(donor_resp_stmt)
                    d_resp_obj = donor_resp_res.scalar_one_or_none()
                    if d_resp_obj:
                        donor_resp_status = d_resp_obj.status

                donor_items.append(
                    MatchCandidateResponseSchema(
                        id=cand.id,
                        rank=cand.rank,
                        candidate_type="DONOR",
                        candidate_id=d_id_str,
                        name=f"Donor #{short}",
                        blood_type=d_btype,
                        compatibility_score=cand.compatibility_score,
                        proximity_score=cand.proximity_score,
                        availability_score=cand.availability_score,
                        ai_score=cand.ai_score,
                        total_score=cand.total_score,
                        distance_km=cand.distance_km,
                        units_available=cand.units_available,
                        status=cand.status.value,
                        donor_response_status=donor_resp_status,
                        explanation=cand.explanation or [],
                        location_display=loc,
                        is_compatible=True,
                    )
                )

        return MatchRunResponseSchema(
            id=run.id,
            emergency_request_id=run.emergency_request_id,
            run_number=run.run_number,
            status=run.status.value,
            model_version=run.model_version,
            algorithm=run.algorithm,
            search_radius_km=run.search_radius_km,
            candidates_evaluated=run.candidates_evaluated,
            donors_matched=run.donors_matched,
            blood_banks_matched=run.blood_banks_matched,
            execution_duration_ms=run.execution_duration_ms,
            created_at=run.created_at,
            blood_banks=bb_items,
            donors=donor_items,
        )

    async def update_candidate_status(
        self,
        candidate_id: uuid.UUID,
        new_status_str: str,
    ) -> MatchCandidateResponseSchema:
        """Updates status of a match candidate (e.g. SHORTLISTED or DISMISSED)."""
        try:
            status_enum = MatchCandidateStatusEnum(new_status_str.upper())
        except ValueError:
            raise RequestNotEligibleForMatchingError(f"Invalid status: {new_status_str}")

        cand = await self.repo.update_candidate_status(candidate_id, status_enum)
        if not cand:
            raise CandidateNotFoundError()

        await self.db.commit()
        await self.db.refresh(cand)

        return MatchCandidateResponseSchema(
            id=cand.id,
            rank=cand.rank,
            candidate_type=cand.candidate_type.value,
            candidate_id=str(cand.donor_id or cand.blood_bank_id),
            name="Candidate",
            blood_type="Unknown",
            compatibility_score=cand.compatibility_score,
            proximity_score=cand.proximity_score,
            availability_score=cand.availability_score,
            ai_score=cand.ai_score,
            total_score=cand.total_score,
            distance_km=cand.distance_km,
            units_available=cand.units_available,
            status=cand.status.value,
            explanation=cand.explanation or [],
            location_display="Updated",
            is_compatible=True,
        )
