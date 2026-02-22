"""
Model Trainer — trains the 3 best industry-standard gradient boosting models
with optional hyperparameter tuning.

Models: XGBoost, LightGBM, CatBoost
These are the top 3 models for tabular/structured data in industry today.
"""
import numpy as np
import pandas as pd
import logging
import joblib
import time
from typing import Dict, Any, Tuple, Optional
from pathlib import Path

from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier

from app.config import RANDOM_STATE, SAVED_MODELS_DIR, OPTUNA_N_TRIALS

logger = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MODEL DEFINITIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MODEL_INFO = {
    "xgboost": {
        "name": "XGBoost",
        "description": "Gradient Boosting framework that sequentially builds trees, each correcting the errors of the previous ensemble. Gold standard for tabular data.",
        "how_it_works": "Starts with a simple prediction, then iteratively adds decision trees. Each new tree is trained on the residual errors (gradients) of the current ensemble. Uses L1/L2 regularization to prevent overfitting.",
        "why_for_churn": "Wins most Kaggle competitions on structured data. Excellent at finding subtle churn signals. Built-in handling of missing values. Regularization prevents overfitting on small datasets.",
        "strengths": "State-of-the-art accuracy, regularization, handles missing values",
        "weaknesses": "More hyperparameters to tune, slower training than LightGBM"
    },
    "lightgbm": {
        "name": "LightGBM",
        "description": "Microsoft's gradient boosting framework that uses histogram-based splits and leaf-wise tree growth for faster training on large datasets.",
        "how_it_works": "Similar to XGBoost but with two key innovations: (1) Histogram-based splitting bins continuous features into buckets, reducing split candidates. (2) Leaf-wise growth picks the leaf with maximum loss reduction, yielding deeper, more accurate trees.",
        "why_for_churn": "10x faster than XGBoost on large datasets. Native categorical feature support. Production-ready with fast inference. Handles the 20+ features in telco data efficiently.",
        "strengths": "Fast training, low memory, native categoricals, great accuracy",
        "weaknesses": "Leaf-wise growth can overfit on small datasets if max_depth isn't controlled"
    },
    "catboost": {
        "name": "CatBoost",
        "description": "Yandex's gradient boosting that natively handles categorical features without pre-encoding. Uses 'ordered boosting' to prevent target leakage.",
        "how_it_works": "Uses symmetric (oblivious) decision trees where the same feature and threshold is used across an entire level. For categoricals, it uses ordered target statistics — each sample's encoding uses only samples that came before it, preventing data leakage.",
        "why_for_churn": "Telco churn data has many categoricals (contract type, payment method, etc.). CatBoost handles them optimally without manual encoding. Ordered boosting gives more reliable predictions.",
        "strengths": "Best categorical handling, no encoding needed, reduced overfitting",
        "weaknesses": "Slower training than LightGBM, larger model files"
    },
}


def build_default_models() -> Dict[str, Any]:
    """Build all 3 models with reasonable default hyperparameters."""
    return {
        "xgboost": XGBClassifier(
            n_estimators=200, max_depth=6, learning_rate=0.1,
            random_state=RANDOM_STATE, eval_metric="logloss",
            use_label_encoder=False, n_jobs=-1
        ),
        "lightgbm": LGBMClassifier(
            n_estimators=200, max_depth=8, learning_rate=0.1,
            random_state=RANDOM_STATE, verbose=-1, n_jobs=-1
        ),
        "catboost": CatBoostClassifier(
            iterations=200, depth=6, learning_rate=0.1,
            random_state=RANDOM_STATE, verbose=0
        ),
    }


def tune_hyperparameters(
    model_name: str,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    n_trials: int = OPTUNA_N_TRIALS
) -> Dict[str, Any]:
    """
    Hyperparameter tuning using Optuna.

    Why Optuna over RandomSearchCV?
    1. Bayesian optimization (TPE sampler) learns from previous trials
    2. Pruning stops unpromising trials early → saves 50%+ compute
    3. More flexible objective functions
    4. Built-in visualization of optimization history
    """
    import optuna
    from sklearn.model_selection import cross_val_score
    optuna.logging.set_verbosity(optuna.logging.WARNING)

    def objective(trial):
        if model_name == "xgboost":
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 100, 500),
                "max_depth": trial.suggest_int("max_depth", 3, 10),
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
                "subsample": trial.suggest_float("subsample", 0.6, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
                "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
                "random_state": RANDOM_STATE,
                "eval_metric": "logloss",
                "use_label_encoder": False,
                "n_jobs": -1,
            }
            model = XGBClassifier(**params)

        elif model_name == "lightgbm":
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 100, 500),
                "max_depth": trial.suggest_int("max_depth", 3, 12),
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
                "num_leaves": trial.suggest_int("num_leaves", 20, 150),
                "subsample": trial.suggest_float("subsample", 0.6, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
                "random_state": RANDOM_STATE,
                "verbose": -1,
                "n_jobs": -1,
            }
            model = LGBMClassifier(**params)

        elif model_name == "catboost":
            params = {
                "iterations": trial.suggest_int("iterations", 100, 500),
                "depth": trial.suggest_int("depth", 3, 10),
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
                "l2_leaf_reg": trial.suggest_float("l2_leaf_reg", 1.0, 10.0),
                "random_state": RANDOM_STATE,
                "verbose": 0,
            }
            model = CatBoostClassifier(**params)

        else:
            return 0.0

        scores = cross_val_score(model, X_train, y_train, cv=3, scoring="f1")
        return scores.mean()

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=n_trials, timeout=120)

    return {
        "best_params": study.best_params,
        "best_score": round(study.best_value, 4),
        "n_trials": len(study.trials),
    }


def train_all_models(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    tune: bool = False,
    progress_callback=None
) -> Dict[str, Any]:
    """
    Train all 3 gradient boosting models and return predictions + metadata.

    Args:
        tune: If True, run Optuna hyperparameter tuning
        progress_callback: Optional callable for progress updates

    Returns:
        Dict with trained models, predictions, training times, and model info
    """
    models = build_default_models()
    results = {}
    total_models = 3
    current = 0

    for name, model in models.items():
        current += 1
        if progress_callback:
            progress_callback(current, total_models, f"Training {MODEL_INFO[name]['name']}...")

        logger.info(f"Training {name}...")
        start_time = time.time()

        # Optional hyperparameter tuning
        tuning_info = None
        if tune:
            logger.info(f"  Tuning {name} with Optuna...")
            tuning_info = tune_hyperparameters(name, X_train, y_train)

            # Rebuild model with best params
            if name == "xgboost":
                model = XGBClassifier(
                    **tuning_info["best_params"],
                    random_state=RANDOM_STATE,
                    eval_metric="logloss",
                    use_label_encoder=False,
                    n_jobs=-1
                )
            elif name == "lightgbm":
                model = LGBMClassifier(
                    **tuning_info["best_params"],
                    random_state=RANDOM_STATE,
                    verbose=-1,
                    n_jobs=-1
                )
            elif name == "catboost":
                model = CatBoostClassifier(
                    **tuning_info["best_params"],
                    random_state=RANDOM_STATE,
                    verbose=0
                )

        model.fit(X_train, y_train)
        train_time = time.time() - start_time

        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        # Save model
        model_path = SAVED_MODELS_DIR / f"{name}.joblib"
        joblib.dump(model, model_path)

        results[name] = {
            "model": model,
            "y_pred": y_pred,
            "y_prob": y_prob,
            "train_time": round(train_time, 2),
            "info": MODEL_INFO[name],
            "tuning_info": tuning_info,
        }

        logger.info(f"  {name} trained in {train_time:.2f}s")

    return results
