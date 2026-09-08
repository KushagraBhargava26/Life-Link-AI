# ai/data/generate_synthetic_donor_dataset.py
# LifeLink AI — Synthetic Donor Response Dataset Generator
# DISCLAIMER: This dataset contains purely synthetic non-clinical operational data
# generated for algorithmic benchmarking, continuous integration, and load testing.
# It does NOT contain real patient or donor personal health information (PHI/PII).

from __future__ import annotations

import argparse
import os
import random
from datetime import datetime, timezone
import numpy as np
import pandas as pd

BLOOD_TYPES = ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"]
URGENCY_LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def generate_synthetic_data(num_samples: int = 1500, random_seed: int = 42) -> pd.DataFrame:
    """
    Generates synthetic donor features and response outcomes based on RFM behavioral models.
    """
    np.random.seed(random_seed)
    random.seed(random_seed)

    records = []

    for i in range(num_samples):
        # Recency: months since last donation (1 to 36 months, weighted towards 3-12)
        recency_months = round(float(np.random.gamma(shape=3.0, scale=3.0)), 1)
        recency_months = max(1.8, min(36.0, recency_months))

        # Frequency: total historical donations (1 to 30)
        frequency = int(np.random.negative_binomial(n=2, p=0.3)) + 1
        frequency = min(35, frequency)

        # Time: months since first registration (must be >= recency)
        time_months = round(recency_months + float(np.random.gamma(shape=2.5, scale=6.0)), 1)
        time_months = max(recency_months + 1.0, min(120.0, time_months))

        # Volume in cc
        monetary_volume_cc = frequency * 250

        # Distance from emergency site in km (1.0 to 50.0 km)
        distance_km = round(float(np.random.exponential(scale=12.0) + 1.5), 1)
        distance_km = min(60.0, distance_km)

        # Blood group
        blood_type = random.choices(
            BLOOD_TYPES, weights=[0.07, 0.38, 0.06, 0.30, 0.02, 0.09, 0.01, 0.07], k=1
        )[0]

        # Urgency level
        urgency = random.choices(URGENCY_LEVELS, weights=[0.10, 0.25, 0.40, 0.25], k=1)[0]

        # Response probability model (Synthetic Ground Truth)
        # Log-odds based on RFM: high frequency, low recency, short distance increase response
        urgency_boost = {"LOW": -0.3, "MEDIUM": 0.0, "HIGH": 0.4, "CRITICAL": 0.8}[urgency]
        z = (
            -0.8
            - 0.08 * recency_months
            + 0.12 * frequency
            + 0.01 * time_months
            - 0.05 * distance_km
            + urgency_boost
            + np.random.normal(0, 0.3)
        )
        prob = 1.0 / (1.0 + np.exp(-z))
        responded = 1 if prob >= 0.50 else 0

        records.append({
            "donor_id": f"syn-donor-{i+1:05d}",
            "blood_type": blood_type,
            "recency_months": recency_months,
            "frequency_donations": frequency,
            "monetary_volume_cc": monetary_volume_cc,
            "time_months": time_months,
            "distance_km": distance_km,
            "urgency_level": urgency,
            "response_propensity_true": round(float(prob), 4),
            "donated_blood": responded,
        })

    df = pd.DataFrame(records)
    return df


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic donor response dataset for LifeLink AI.")
    parser.add_argument("--samples", type=int, default=1500, help="Number of synthetic records to generate")
    parser.add_argument("--output", type=str, default="synthetic_donor_dataset.csv", help="Output CSV filename")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, args.output)

    df = generate_synthetic_data(num_samples=args.samples)
    df.to_csv(output_path, index=False)

    pos = int(df["donated_blood"].sum())
    print(f"Generated {len(df)} synthetic records -> {output_path}")
    print(f"Positive responses: {pos} ({pos/len(df)*100:.1f}%), Negative: {len(df)-pos} ({(len(df)-pos)/len(df)*100:.1f}%)")


if __name__ == "__main__":
    main()
