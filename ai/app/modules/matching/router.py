# ai/app/modules/matching/router.py
# LifeLink AI — Blood Matching & Ranking Engine Router
# Architecture Reference: ARCHITECTURE.md Section 17 (AI Architecture)

from __future__ import annotations
from fastapi import APIRouter, status
from app.modules.matching.schemas import (
    RankDonorsRequest,
    RankDonorsResponse,
    RankedDonorCandidate,
)
from app.modules.matching.propensity import get_propensity_model

router = APIRouter()


@router.post(
    "/rank",
    response_model=RankDonorsResponse,
    status_code=status.HTTP_200_OK,
    summary="Rank pre-filtered compatible donor candidates",
)
async def rank_candidates(payload: RankDonorsRequest) -> RankDonorsResponse:
    """
    Ranks compatible donor candidates using the trained response propensity model
    and deterministic distance/availability scoring.
    """
    propensity_model = get_propensity_model()
    radius = max(1.0, payload.search_radius_km)
    scored_candidates: list[dict] = []

    for candidate in payload.candidates:
        # 1. Propensity Score from ML model
        propensity = propensity_model.predict_propensity(
            recency_months=candidate.recency_months,
            frequency_donations=candidate.frequency_donations,
            time_months=candidate.time_months,
        )

        # 2. Proximity Score (Linear decay over radius)
        if candidate.distance_km is not None:
            dist = max(0.0, candidate.distance_km)
            proximity = max(0.0, 1.0 - (dist / radius))
        else:
            proximity = 0.50  # Neutral fallback for missing coordinates

        # 3. Compatibility & Availability Scores
        compat = candidate.compatibility_score
        avail = candidate.availability_score

        # 4. Composite Scoring per ADR-004
        # 40% Compatibility, 30% Proximity, 20% Availability, 10% Propensity
        total = (compat * 0.40) + (proximity * 0.30) + (avail * 0.20) + (propensity * 0.10)
        total = round(min(1.0, max(0.0, total)), 4)

        # 5. Formulate Human-Readable Explanations
        explanation: list[str] = []
        if compat >= 0.99:
            explanation.append(f"Exact ABO/Rh match ({candidate.blood_type})")
        else:
            explanation.append(f"Compatible universal donor group ({candidate.blood_type})")

        if candidate.distance_km is not None:
            explanation.append(f"Located {candidate.distance_km:.1f} km from emergency facility")
        else:
            explanation.append("Local municipality match (coordinates pending)")

        explanation.append("Verified active and eligible (no cooling period cooldown)")

        if propensity >= 0.60:
            explanation.append(f"High historical response propensity ({int(propensity * 100)}%)")
        elif propensity >= 0.40:
            explanation.append(f"Moderate historical response propensity ({int(propensity * 100)}%)")
        else:
            explanation.append(f"Standard response baseline ({int(propensity * 100)}%)")

        scored_candidates.append({
            "donor_id": candidate.donor_id,
            "total_score": total,
            "compatibility_score": round(compat, 4),
            "proximity_score": round(proximity, 4),
            "availability_score": round(avail, 4),
            "propensity_score": round(propensity, 4),
            "distance_km": round(candidate.distance_km, 2) if candidate.distance_km is not None else None,
            "explanation": explanation,
        })

    # Sort descending by composite score
    scored_candidates.sort(key=lambda x: x["total_score"], reverse=True)

    ranked_items: list[RankedDonorCandidate] = []
    for idx, item in enumerate(scored_candidates, start=1):
        ranked_items.append(
            RankedDonorCandidate(
                donor_id=item["donor_id"],
                rank=idx,
                total_score=item["total_score"],
                compatibility_score=item["compatibility_score"],
                proximity_score=item["proximity_score"],
                availability_score=item["availability_score"],
                propensity_score=item["propensity_score"],
                distance_km=item["distance_km"],
                explanation=item["explanation"],
            )
        )

    return RankDonorsResponse(
        request_id=payload.request_id,
        model_version=propensity_model.model_version if propensity_model.is_loaded else "deterministic-fallback",
        algorithm="calibrated_logistic_regression_hybrid" if propensity_model.is_loaded else "deterministic_rule_engine",
        candidates_ranked=len(ranked_items),
        candidates=ranked_items,
    )
