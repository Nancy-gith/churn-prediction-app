"""
Model Evaluator — computes all evaluation metrics, confusion matrices,
and ROC curve data for the frontend.
"""
import numpy as np
from typing import Dict, Any
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix, roc_curve
)


def evaluate_model(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: np.ndarray,
    model_name: str
) -> Dict[str, Any]:
    """
    Compute comprehensive evaluation metrics for a single model.

    Metrics explained:
    - Accuracy: (TP+TN)/(TP+TN+FP+FN) — misleading with imbalanced data!
    - Precision: TP/(TP+FP) — of predicted churners, how many actually churned?
    - Recall: TP/(TP+FN) — of actual churners, how many did we catch? ← MOST IMPORTANT
    - F1-Score: 2*(P*R)/(P+R) — harmonic mean, balances precision and recall
    - ROC-AUC: Area under ROC curve — model's ranking ability across all thresholds

    Why Recall matters most for churn:
    - False Negative cost >> False Positive cost
    - Missing a churner = lost customer (high LTV loss)
    - False alarm = send retention offer (low cost)
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    y_prob = np.array(y_prob)

    # Core metrics
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    auc = roc_auc_score(y_true, y_prob) if len(np.unique(y_true)) > 1 else 0.0

    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()

    # ROC curve data points
    fpr, tpr, thresholds = roc_curve(y_true, y_prob)
    # Downsample for frontend (100 points)
    step = max(1, len(fpr) // 100)
    roc_data = [
        {"fpr": round(float(fpr[i]), 4), "tpr": round(float(tpr[i]), 4)}
        for i in range(0, len(fpr), step)
    ]

    return {
        "model_name": model_name,
        "metrics": {
            "accuracy": round(float(acc), 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1_score": round(float(f1), 4),
            "roc_auc": round(float(auc), 4),
        },
        "confusion_matrix": {
            "tn": int(tn), "fp": int(fp),
            "fn": int(fn), "tp": int(tp),
            "labels": ["No Churn", "Churn"],
        },
        "roc_curve": roc_data,
    }


def evaluate_all_models(results: Dict, y_test: np.ndarray) -> Dict[str, Any]:
    """Evaluate all trained models and return comparison data."""
    evaluations = {}
    comparison_table = []

    for name, result in results.items():
        eval_result = evaluate_model(
            y_true=y_test,
            y_pred=result["y_pred"],
            y_prob=result["y_prob"],
            model_name=result["info"]["name"]
        )

        eval_result["train_time"] = result["train_time"]
        eval_result["info"] = result["info"]
        eval_result["tuning_info"] = result.get("tuning_info")

        evaluations[name] = eval_result

        # Build comparison row
        comparison_table.append({
            "model": result["info"]["name"],
            "model_key": name,
            **eval_result["metrics"],
            "train_time": result["train_time"],
        })

    # Sort by F1 score (best balance of precision and recall)
    comparison_table.sort(key=lambda x: x["f1_score"], reverse=True)

    # Find best model
    best_model_key = comparison_table[0]["model_key"]

    return {
        "evaluations": evaluations,
        "comparison_table": comparison_table,
        "best_model": best_model_key,
        "best_model_name": comparison_table[0]["model"],
        "recommendation": (
            f"The best model is {comparison_table[0]['model']} with "
            f"F1={comparison_table[0]['f1_score']:.4f} and "
            f"Recall={evaluations[best_model_key]['metrics']['recall']:.4f}. "
            f"Recall is the most critical metric for churn — it measures how many "
            f"actual churners we catch. A missed churner costs more than a false alarm."
        ),
    }
