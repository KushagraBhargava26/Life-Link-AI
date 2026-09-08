# ai/app/modules/matching/propensity.py
"""
LifeLink AI — Donor Response Propensity Inference Service
Dataset: UCI Blood Transfusion Service Center (CC BY 4.0)
Model: donor-response-v1
"""

from __future__ import annotations
import os
import json
import logging
from typing import Any, Optional
import joblib
import numpy as np

logger = logging.getLogger("lifelink.ai.propensity")

MODEL_PATHS = [
    os.path.join(os.getcwd(), "models", "donor-response-v1", "donor_response_v1.joblib"),
    os.path.join(os.getcwd(), "ai", "models", "donor-response-v1", "donor_response_v1.joblib"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "models", "donor-response-v1", "donor_response_v1.joblib"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "models", "donor-response-v1", "donor_response_v1.joblib"),
    "/app/models/donor-response-v1/donor_response_v1.joblib",
]

class DonorPropensityModel:
    """Loads and serves the donor response propensity model."""

    def __init__(self) -> None:
        self.pipeline: Any = None
        self.model_version: str = "donor-response-v1"
        self.is_loaded: bool = False
        self._load_model()

    def _load_model(self) -> None:
        for path in MODEL_PATHS:
            resolved = os.path.abspath(path)
            if os.path.exists(resolved):
                try:
                    self.pipeline = joblib.load(resolved)
                    self.is_loaded = True
                    logger.info("Loaded donor response propensity model from %s", resolved)
                    return
                except Exception as e:
                    logger.warning("Failed to load model from %s: %s", resolved, e)
        logger.warning("No pre-trained donor response model found. Fallback heuristic scoring enabled.")

    def predict_propensity(
        self,
        recency_months: float,
        frequency_donations: int,
        time_months: float,
    ) -> float:
        """
        Predict donor response propensity probability in [0.0, 1.0].
        Features:
        - recency_months: months since last donation (clamped >= 0)
        - frequency_donations: total lifetime donations (clamped >= 0)
        - time_months: months since first donation / registration (clamped >= recency_months)
        """
        r = max(0.0, float(recency_months))
        f = max(0, int(frequency_donations))
        t = max(r, float(time_months))

        if self.is_loaded and self.pipeline is not None:
            try:
                features = np.array([[r, f, t]], dtype=float)
                prob = float(self.pipeline.predict_proba(features)[0, 1])
                return round(min(1.0, max(0.0, prob)), 4)
            except Exception as e:
                logger.error("Error during model inference: %s", e)

        # Robust heuristic fallback based on RFM principles
        # More donations (F) and lower recency (R) yield higher propensity
        base = 0.40
        recency_factor = max(0.0, 0.35 - (r * 0.01))
        freq_factor = min(0.25, f * 0.05)
        fallback_prob = min(0.95, max(0.05, base + recency_factor + freq_factor))
        return round(fallback_prob, 4)

_propensity_singleton: Optional[DonorPropensityModel] = None

def get_propensity_model() -> DonorPropensityModel:
    global _propensity_singleton
    if _propensity_singleton is None:
        _propensity_singleton = DonorPropensityModel()
    return _propensity_singleton
