"""LifeLink AI Gateway Service.
Mediates all communication between backend and internal AI microservice.
Architecture Reference: ARCHITECTURE.md Section 17 & 29.
"""

from __future__ import annotations
import logging
from typing import Any, Optional, List, Dict
import httpx
from app.config import settings

logger = logging.getLogger("lifelink.backend.ai_gateway")


class AiGatewayService:
    """Client for the internal LifeLink AI microservice."""

    def __init__(self) -> None:
        self.base_url = settings.AI_SERVICE_URL or "http://ai-service:8001"
        self.api_key = settings.AI_SERVICE_API_KEY
        self.timeout = float(getattr(settings, "AI_MATCHING_TIMEOUT_SECONDS", 5.0))

    async def rank_donor_candidates(
        self,
        request_id: str,
        blood_type_required: str,
        urgency_level: str,
        search_radius_km: float,
        candidates: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """
        Submits candidate feature vectors to AI service for response propensity ranking.
        Returns None if AI service is unreachable or times out (enabling seamless fallback).
        """
        if not candidates:
            return {
                "request_id": request_id,
                "model_version": "donor-response-v1",
                "algorithm": "calibrated_logistic_regression_hybrid",
                "candidates_ranked": 0,
                "candidates": [],
            }

        headers = {
            "X-AI-Service-Key": self.api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "request_id": str(request_id),
            "blood_type_required": blood_type_required,
            "urgency_level": urgency_level,
            "search_radius_km": search_radius_km,
            "candidates": candidates,
        }

        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
                resp = await client.post("/matching/rank", json=payload, headers=headers)
                if resp.status_code == 200:
                    return resp.json()
                logger.warning("AI ranking returned non-200 status %d: %s", resp.status_code, resp.text)
                return None
        except httpx.TimeoutException:
            logger.warning("AI ranking request timed out after %.1fs; invoking deterministic fallback", self.timeout)
            return None
        except Exception as e:
            logger.warning("AI ranking service unavailable (%s); invoking deterministic fallback", e)
            return None
