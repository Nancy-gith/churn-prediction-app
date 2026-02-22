"""
SHAP Service — computes SHAP values for model explanations.

SHAP (SHapley Additive exPlanations) is based on game theory:
- Each feature is a "player" in a cooperative game
- The SHAP value tells you each feature's contribution to the prediction
- Positive SHAP value → pushes prediction toward churn
- Negative SHAP value → pushes prediction toward no churn
"""
import numpy as np
import pandas as pd
import shap
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def compute_shap_global(model, X_train: pd.DataFrame, model_name: str) -> Dict[str, Any]:
    """
    Compute global SHAP feature importance across all predictions.

    Uses TreeExplainer for all 3 models (XGBoost, LightGBM, CatBoost)
    since they are all tree-based — fast and exact.

    Returns: feature importance ranking with SHAP values for visualization.
    """
    try:
        # TreeExplainer: O(TLD²) — fast, exact for tree models
        explainer = shap.TreeExplainer(model)
        # Use a sample to avoid memory issues on large datasets
        sample = X_train.sample(min(500, len(X_train)), random_state=42)
        shap_values = explainer.shap_values(sample)

        # For binary classification, shap_values might be a list [class0, class1]
        if isinstance(shap_values, list):
            shap_values = shap_values[1]  # Use class 1 (churn) values

        # Compute mean absolute SHAP values (global importance)
        shap_array = np.array(shap_values)
        mean_abs_shap = np.abs(shap_array).mean(axis=0)

        feature_names = list(X_train.columns)
        importance_data = sorted(
            [{"feature": name, "importance": round(float(val), 4)}
             for name, val in zip(feature_names, mean_abs_shap)],
            key=lambda x: x["importance"],
            reverse=True
        )

        return {
            "type": "global",
            "model_name": model_name,
            "feature_importance": importance_data[:20],  # Top 20
            "total_features": len(feature_names),
        }

    except Exception as e:
        logger.error(f"SHAP computation failed for {model_name}: {str(e)}")
        return {"error": str(e), "model_name": model_name}


def compute_shap_individual(
    model, customer_df: pd.DataFrame, X_background: pd.DataFrame, model_name: str
) -> Dict[str, Any]:
    """
    Compute SHAP values for a single customer prediction.
    Used on the Predict page to explain why the model made its prediction.

    Returns: top features driving this specific prediction.
    """
    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(customer_df)

        if isinstance(shap_values, list):
            shap_values = shap_values[1]

        shap_array = np.array(shap_values).flatten()
        feature_names = list(customer_df.columns)

        contributions = sorted(
            [{"feature": name, "shap_value": round(float(val), 4),
              "direction": "increases churn" if val > 0 else "decreases churn"}
             for name, val in zip(feature_names, shap_array)],
            key=lambda x: abs(x["shap_value"]),
            reverse=True
        )

        return {
            "type": "individual",
            "top_reasons": contributions[:10],
            "all_contributions": contributions,
        }

    except Exception as e:
        logger.error(f"Individual SHAP failed: {str(e)}")
        return {"error": str(e)}
