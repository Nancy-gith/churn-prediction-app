"""
Predictor — loads trained models and makes predictions for individual customers.
Handles feature transformation to match the training pipeline.
"""
import numpy as np
import pandas as pd
import joblib
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from app.config import SAVED_MODELS_DIR

logger = logging.getLogger(__name__)


def predict_single_customer(
    customer_data: Dict[str, Any],
    model_name: str,
    scaler,
    encoders: dict,
    feature_names: list,
    numeric_cols: list,
) -> Dict[str, Any]:
    """
    Predict churn for a single customer using a trained model.

    Steps:
    1. Convert input dict to DataFrame row
    2. Apply same encoding as training (label + one-hot)
    3. Apply same scaling as training
    4. Predict with selected model
    5. Return probability + risk level

    Args:
        customer_data: Dict with customer feature values
        model_name: Which trained model to use
        scaler: Fitted StandardScaler from training
        encoders: Fitted encoders from training
        feature_names: Feature column names after encoding
        numeric_cols: Numeric column names for scaling
    """
    # ── Step 1: Create single-row DataFrame ──
    df = pd.DataFrame([customer_data])

    # ── Step 2: Apply encodings ──
    # Label encode binary columns
    for col, le in encoders.get("label_encoders", {}).items():
        if col in df.columns:
            try:
                df[col] = le.transform(df[col])
            except ValueError:
                # Unseen category: use most common class
                df[col] = 0

    # One-hot encode multi-category columns
    for ohe_info in encoders.get("one_hot_columns", []):
        original_col = ohe_info["original"]
        new_cols = ohe_info["new_columns"]

        if original_col in df.columns:
            dummies = pd.get_dummies(df[original_col], prefix=original_col, dtype=int)
            df = pd.concat([df, dummies], axis=1)
            df = df.drop(columns=[original_col])

    # ── Step 3: Align columns with training data ──
    for col in feature_names:
        if col not in df.columns:
            df[col] = 0

    df = df[feature_names]

    # ── Step 4: Scale numeric features ──
    scale_cols = [c for c in numeric_cols if c in df.columns]
    if scale_cols and scaler is not None:
        df[scale_cols] = scaler.transform(df[scale_cols])

    # ── Step 5: Load model and predict ──
    model_path = SAVED_MODELS_DIR / f"{model_name}.joblib"
    model = joblib.load(model_path)
    prediction = int(model.predict(df)[0])
    probability = float(model.predict_proba(df)[0][1])

    # ── Step 6: Determine risk level ──
    if probability < 0.3:
        risk_level = "low"
        risk_label = "Low Risk"
        risk_color = "#22c55e"  # green
    elif probability < 0.6:
        risk_level = "medium"
        risk_label = "Medium Risk"
        risk_color = "#eab308"  # yellow
    else:
        risk_level = "high"
        risk_label = "High Risk"
        risk_color = "#ef4444"  # red

    return {
        "prediction": "Churn" if prediction == 1 else "No Churn",
        "prediction_numeric": prediction,
        "probability": round(probability, 4),
        "probability_percentage": round(probability * 100, 1),
        "risk_level": risk_level,
        "risk_label": risk_label,
        "risk_color": risk_color,
        "model_used": model_name,
    }
