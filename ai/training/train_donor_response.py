"""
LifeLink AI — Donor Response Propensity Model Training Script
Dataset: UCI Blood Transfusion Service Center (CC BY 4.0)
Model: donor-response-v1
"""

import json
import os
import sys
import zipfile
import urllib.request
from datetime import datetime, timezone
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
AI_DIR = os.path.join(PROJECT_ROOT, "ai")
DATA_DIR = os.path.join(AI_DIR, "training", "data")
DATA_PATH = os.path.join(DATA_DIR, "transfusion.data")
MODEL_DIR = os.path.join(AI_DIR, "models", "donor-response-v1")
MODEL_PATH = os.path.join(MODEL_DIR, "donor_response_v1.joblib")
METADATA_PATH = os.path.join(MODEL_DIR, "metadata.json")

DATASET_URLS = [
    "https://archive.ics.uci.edu/static/public/176/blood+transfusion+service+center.zip",
    "https://raw.githubusercontent.com/datasets/blood-transfusion/master/data/blood-transfusion-service-center.csv",
]

FEATURE_NAMES = [
    "recency_months",
    "frequency_donations",
    "monetary_volume_cc",
    "time_months",
]
TARGET_COL = "donated_blood"

def download_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(DATA_PATH):
        print(f"Dataset already cached at {DATA_PATH}")
        return

    # Try UCI zip archive first
    zip_path = os.path.join(DATA_DIR, "transfusion.zip")
    headers = {"User-Agent": "LifeLinkAI-Trainer/1.0"}

    for url in DATASET_URLS:
        try:
            print(f"Attempting download from: {url}")
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read()
                if url.endswith(".zip"):
                    with open(zip_path, "wb") as f:
                        f.write(content)
                    with zipfile.ZipFile(zip_path, "r") as zf:
                        zf.extractall(DATA_DIR)
                    if os.path.exists(zip_path):
                        os.remove(zip_path)
                else:
                    with open(DATA_PATH, "wb") as f:
                        f.write(content)
            if os.path.exists(DATA_PATH):
                print(f"Successfully obtained dataset: {DATA_PATH}")
                return
        except Exception as e:
            print(f"Download failed from {url}: {e}")

    # Fallback via OpenML
    try:
        from sklearn.datasets import fetch_openml
        print("Attempting to fetch dataset via OpenML (ID 1464)...")
        bunch = fetch_openml(data_id=1464, as_frame=True, parser="auto")
        df = bunch.frame
        df.to_csv(DATA_PATH, index=False)
        print("Successfully fetched dataset via OpenML.")
        return
    except Exception as e:
        print(f"OpenML fetch failed: {e}")

    if not os.path.exists(DATA_PATH):
        raise RuntimeError("Unable to download or fetch UCI Blood Transfusion dataset.")

def load_and_preprocess() -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    download_data()
    df = pd.read_csv(DATA_PATH)
    if len(df.columns) == 5:
        df.columns = FEATURE_NAMES + [TARGET_COL]
    else:
        df.rename(columns={
            df.columns[0]: "recency_months",
            df.columns[1]: "frequency_donations",
            df.columns[2]: "monetary_volume_cc",
            df.columns[3]: "time_months",
            df.columns[4]: TARGET_COL,
        }, inplace=True)

    df[TARGET_COL] = df[TARGET_COL].astype(str).str.strip()
    df[TARGET_COL] = df[TARGET_COL].apply(lambda x: 1 if str(x) in ["1", "yes", "true", "2"] else 0)

    X = df[["recency_months", "frequency_donations", "time_months"]].values
    y = df[TARGET_COL].values.astype(int)

    return df, X, y

def train_and_evaluate():
    print("=" * 60)
    print("LIFELINK AI — TRAINING DONOR RESPONSE PROPENSITY MODEL")
    print("Dataset: UCI Blood Transfusion Service Center (CC BY 4.0)")
    print("=" * 60)

    df, X, y = load_and_preprocess()
    n_samples, n_features = X.shape
    pos_samples = int(np.sum(y))
    neg_samples = n_samples - pos_samples

    print(f"Dataset summary: {n_samples} records, {n_features} features")
    print(f"Class distribution: {pos_samples} donated ({pos_samples/n_samples*100:.1f}%), {neg_samples} did not ({neg_samples/n_samples*100:.1f}%)")

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", LogisticRegression(class_weight="balanced", random_state=42, C=1.0, max_iter=1000)),
    ])

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    oof_probs = cross_val_predict(pipeline, X, y, cv=cv, method="predict_proba")[:, 1]
    oof_preds = (oof_probs >= 0.5).astype(int)

    acc = accuracy_score(y, oof_preds)
    prec = precision_score(y, oof_preds, zero_division=0)
    rec = recall_score(y, oof_preds, zero_division=0)
    f1 = f1_score(y, oof_preds, zero_division=0)
    roc_auc = roc_auc_score(y, oof_probs)
    pr_auc = average_precision_score(y, oof_probs)
    brier = brier_score_loss(y, oof_probs)

    print("\n--- 5-Fold Cross-Validation Metrics ---")
    print(f"Accuracy:        {acc:.4f}")
    print(f"Precision:       {prec:.4f}")
    print(f"Recall:          {rec:.4f}")
    print(f"F1 Score:        {f1:.4f}")
    print(f"ROC-AUC:         {roc_auc:.4f}")
    print(f"PR-AUC:          {pr_auc:.4f}")
    print(f"Brier Score:     {brier:.4f}")

    pipeline.fit(X, y)

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"\nModel artifact saved to: {MODEL_PATH}")

    metadata = {
        "model_name": "donor_response_propensity",
        "model_version": "donor-response-v1",
        "algorithm": "StandardScaler + LogisticRegression(class_weight='balanced')",
        "dataset_name": "UCI Blood Transfusion Service Center",
        "dataset_license": "CC BY 4.0",
        "dataset_citation": "Yeh, I-Cheng, Yang, King-Jang, and Ting, Tao-Ming, 'Knowledge discovery on RFM model using Bernoulli sequence,' Expert Systems with Applications, 2008.",
        "dataset_records": int(n_samples),
        "target_variable": "donated_blood (1 = donated in target month, 0 = did not)",
        "features_trained": ["recency_months", "frequency_donations", "time_months"],
        "feature_dropped_collinear": "monetary_volume_cc (strictly 250 * frequency)",
        "train_validation_strategy": "5-fold Stratified Cross-Validation",
        "metrics": {
            "accuracy": round(float(acc), 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1": round(float(f1), 4),
            "roc_auc": round(float(roc_auc), 4),
            "pr_auc": round(float(pr_auc), 4),
            "brier_score": round(float(brier), 4),
        },
        "trained_at_utc": datetime.now(timezone.utc).isoformat(),
        "limitations": "Model estimates historical response propensity from RFM features; does not determine medical compatibility or guarantee real-world donor response.",
    }

    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"Metadata saved to: {METADATA_PATH}")
    print("=" * 60)
    print("TRAINING & EVALUATION COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    train_and_evaluate()
