"""
API Routes — all endpoints for the Churn Prediction App.

Endpoints:
  POST /api/upload          — Upload CSV dataset
  GET  /api/load-default    — Load default dataset
  GET  /api/dataset-preview — Preview loaded dataset
  GET  /api/cleaning-report — Get data cleaning report
  POST /api/clean           — Clean the dataset
  GET  /api/eda             — Get all EDA charts
  POST /api/train           — Train all ML models
  GET  /api/models          — Get available trained models
  GET  /api/evaluation      — Get model evaluation results
  GET  /api/shap/{model}    — Get SHAP feature importance
  POST /api/predict         — Predict churn for a customer
  POST /api/quick-predict   — Quick predict: auto-clean + use saved models
"""
import os
import logging
import joblib
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

from app.config import DATA_DIR, TARGET_COLUMN, SAVED_MODELS_DIR
from app.services.dataset_service import (
    load_default_dataset, load_uploaded_dataset, get_dataset_preview
)
from app.core.data_pipeline import (
    get_cleaning_report, clean_data, prepare_data_for_training
)
from app.core.eda import compute_all_eda
from app.models.trainer import train_all_models, MODEL_INFO
from app.models.evaluator import evaluate_all_models
from app.models.predictor import predict_single_customer
from app.services.shap_service import compute_shap_global, compute_shap_individual

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# In-memory state (for simplicity in development)
# In production, use Redis or a database
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
app_state = {
    "raw_df": None,
    "cleaned_df": None,
    "cleaning_report": None,
    "training_data": None,
    "model_results": None,
    "evaluation_results": None,
}


# ── Pydantic models ──
class PredictionRequest(BaseModel):
    model_config = {"protected_namespaces": ()}
    model_name: str = "xgboost"
    customer_data: Dict[str, Any]


class TrainRequest(BaseModel):
    tune_hyperparameters: bool = False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DATASET ENDPOINTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """Upload a CSV file as the dataset."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    save_path = DATA_DIR / file.filename
    content = await file.read()

    with open(save_path, "wb") as f:
        f.write(content)

    try:
        df = load_uploaded_dataset(str(save_path))
        app_state["raw_df"] = df
        app_state["cleaned_df"] = None
        app_state["training_data"] = None
        app_state["model_results"] = None
        app_state["evaluation_results"] = None

        return {
            "status": "success",
            "message": f"Uploaded {file.filename} with {len(df)} rows",
            "preview": get_dataset_preview(df),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSV: {str(e)}")


@router.get("/load-default")
async def load_default():
    """Load the default telco churn dataset."""
    try:
        df = load_default_dataset()
        app_state["raw_df"] = df
        app_state["cleaned_df"] = None
        app_state["training_data"] = None
        app_state["model_results"] = None
        app_state["evaluation_results"] = None

        return {
            "status": "success",
            "message": f"Loaded default dataset with {len(df)} rows",
            "preview": get_dataset_preview(df),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading dataset: {str(e)}")


@router.get("/dataset-preview")
async def dataset_preview():
    """Get current dataset preview."""
    if app_state["raw_df"] is None:
        raise HTTPException(status_code=404, detail="No dataset loaded. Upload or load default first.")

    return get_dataset_preview(app_state["raw_df"])


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DATA CLEANING ENDPOINTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get("/cleaning-report")
async def get_cleaning_report_endpoint():
    """Get the data cleaning report (before vs after)."""
    if app_state["cleaning_report"] is not None:
        return app_state["cleaning_report"]

    if app_state["raw_df"] is None:
        raise HTTPException(status_code=404, detail="No dataset loaded")

    # Return pre-cleaning analysis
    report = get_cleaning_report(app_state["raw_df"])
    return {"before": report, "cleaned": False}


@router.post("/clean")
async def clean_dataset():
    """Run the full data cleaning pipeline."""
    if app_state["raw_df"] is None:
        raise HTTPException(status_code=404, detail="No dataset loaded")

    try:
        cleaned_df, cleaning_report = clean_data(app_state["raw_df"])
        app_state["cleaned_df"] = cleaned_df
        app_state["cleaning_report"] = cleaning_report

        return {
            "status": "success",
            "message": "Data cleaned successfully",
            "report": cleaning_report,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleaning failed: {str(e)}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EDA ENDPOINTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get("/eda")
async def get_eda():
    """Get all EDA charts as JSON data."""
    df = app_state["cleaned_df"] if app_state["cleaned_df"] is not None else app_state["raw_df"]

    if df is None:
        raise HTTPException(status_code=404, detail="No dataset loaded")

    try:
        eda_results = compute_all_eda(df)
        return eda_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"EDA failed: {str(e)}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MODEL TRAINING ENDPOINTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.post("/train")
async def train_models(request: TrainRequest):
    """
    Train all 3 ML models on the cleaned dataset.

    Set tune_hyperparameters=true for Optuna optimization
    (takes longer but can improve results by 2-5%).
    """
    df = app_state["cleaned_df"]
    if df is None:
        raise HTTPException(
            status_code=400,
            detail="Dataset not cleaned yet. Run /api/clean first."
        )

    try:
        # Prepare data (encode, split, scale, SMOTE)
        training_data = prepare_data_for_training(df)
        app_state["training_data"] = training_data

        # Train all models
        results = train_all_models(
            X_train=training_data["X_train"],
            y_train=training_data["y_train"],
            X_test=training_data["X_test"],
            y_test=training_data["y_test"],
            tune=request.tune_hyperparameters,
        )
        app_state["model_results"] = results

        # Evaluate all models
        evaluation = evaluate_all_models(results, training_data["y_test"])
        app_state["evaluation_results"] = evaluation

        return {
            "status": "success",
            "message": f"Trained {len(results)} models successfully",
            "evaluation": evaluation,
            "encoding_info": training_data["encoding_info"],
            "smote_info": training_data["smote_info"],
        }

    except Exception as e:
        logger.error(f"Training failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")


@router.get("/models")
async def get_available_models():
    """List available models and their info."""
    if app_state["evaluation_results"] is None:
        return {
            "trained": False,
            "available_models": list(MODEL_INFO.keys()),
            "model_info": MODEL_INFO,
        }

    return {
        "trained": True,
        "available_models": list(app_state["model_results"].keys()),
        "model_info": MODEL_INFO,
        "best_model": app_state["evaluation_results"]["best_model"],
    }


@router.get("/evaluation")
async def get_evaluation():
    """Get model evaluation results."""
    if app_state["evaluation_results"] is None:
        raise HTTPException(status_code=404, detail="No models trained yet")

    return app_state["evaluation_results"]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SHAP ENDPOINTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get("/shap/{model_name}")
async def get_shap(model_name: str):
    """Get SHAP feature importance for a specific model."""
    if app_state["model_results"] is None:
        raise HTTPException(status_code=404, detail="No models trained yet")

    if model_name not in app_state["model_results"]:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")

    try:
        model = app_state["model_results"][model_name]["model"]
        X_train = app_state["training_data"]["X_train"]

        shap_result = compute_shap_global(model, X_train, model_name)
        return shap_result

    except Exception as e:
        logger.error(f"SHAP failed for {model_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"SHAP computation failed: {str(e)}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PREDICTION ENDPOINTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.post("/predict")
async def predict(request: PredictionRequest):
    """
    Predict churn for a single customer.

    Requires model training to be completed first.
    Accepts all customer features in customer_data dict.
    Returns prediction, probability, risk level, and SHAP explanation.
    """
    if app_state["training_data"] is None or app_state["model_results"] is None:
        raise HTTPException(
            status_code=400,
            detail="Models not trained yet. Run /api/train first."
        )

    model_name = request.model_name
    if model_name not in app_state["model_results"]:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")

    try:
        training_data = app_state["training_data"]

        # Make prediction
        prediction_result = predict_single_customer(
            customer_data=request.customer_data,
            model_name=model_name,
            scaler=training_data["scaler"],
            encoders=training_data["encoders"],
            feature_names=training_data["feature_names"],
            numeric_cols=training_data["numeric_cols"],
        )

        # Compute SHAP explanation for this prediction
        try:
            model = app_state["model_results"][model_name]["model"]
            X_train = training_data["X_train"]

            # Build the encoded customer dataframe
            customer_df = pd.DataFrame([request.customer_data])

            # Apply encoding
            from app.core.data_pipeline import encode_features
            encoders = training_data["encoders"]

            for col, le in encoders.get("label_encoders", {}).items():
                if col in customer_df.columns:
                    try:
                        customer_df[col] = le.transform(customer_df[col])
                    except ValueError:
                        customer_df[col] = 0

            for ohe_info in encoders.get("one_hot_columns", []):
                original_col = ohe_info["original"]
                if original_col in customer_df.columns:
                    dummies = pd.get_dummies(customer_df[original_col], prefix=original_col, dtype=int)
                    customer_df = pd.concat([customer_df, dummies], axis=1)
                    customer_df = customer_df.drop(columns=[original_col])

            for col in training_data["feature_names"]:
                if col not in customer_df.columns:
                    customer_df[col] = 0
            customer_df = customer_df[training_data["feature_names"]]

            scale_cols = [c for c in training_data["numeric_cols"] if c in customer_df.columns]
            if scale_cols:
                customer_df[scale_cols] = training_data["scaler"].transform(customer_df[scale_cols])

            shap_result = compute_shap_individual(model, customer_df, X_train, model_name)
            prediction_result["shap_explanation"] = shap_result
        except Exception as shap_error:
            logger.warning(f"SHAP individual explanation failed: {shap_error}")
            prediction_result["shap_explanation"] = {"error": str(shap_error)}

        return prediction_result

    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# QUICK PREDICT ENDPOINT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get("/quick-predict/status")
async def quick_predict_status():
    """
    Check which saved models are available on disk for quick prediction.
    This lets the frontend know if Quick Predict is possible.
    """
    available = []
    model_files = {
        "xgboost": "xgboost.joblib",
        "lightgbm": "lightgbm.joblib",
        "catboost": "catboost.joblib",
    }
    for name, filename in model_files.items():
        if (SAVED_MODELS_DIR / filename).exists():
            available.append(name)

    return {
        "available": len(available) > 0,
        "models": available,
        "dataset_loaded": app_state["raw_df"] is not None,
    }


@router.post("/quick-predict")
async def quick_predict(request: PredictionRequest):
    """
    Quick Predict — skip the full pipeline.

    Automatically:
    1. Loads default dataset if none loaded
    2. Cleans the data
    3. Prepares training data (to get scaler + encoders)
    4. Uses SAVED models from disk (no re-training!)
    5. Predicts and returns the result

    This is the shortcut endpoint so users can predict immediately
    after uploading a dataset, without going through cleaning → EDA → training.
    """
    model_name = request.model_name

    # ── Step 1: Ensure dataset is loaded ──
    if app_state["raw_df"] is None:
        try:
            df = load_default_dataset()
            app_state["raw_df"] = df
            logger.info("Quick predict: auto-loaded default dataset")
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"No dataset loaded and could not load default: {str(e)}"
            )

    # ── Step 2: Clean data if not already cleaned ──
    if app_state["cleaned_df"] is None:
        try:
            cleaned_df, cleaning_report = clean_data(app_state["raw_df"])
            app_state["cleaned_df"] = cleaned_df
            app_state["cleaning_report"] = cleaning_report
            logger.info("Quick predict: auto-cleaned dataset")
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Auto-cleaning failed: {str(e)}"
            )

    # ── Step 3: Prepare training data (for scaler + encoders) if not already done ──
    if app_state["training_data"] is None:
        try:
            training_data = prepare_data_for_training(app_state["cleaned_df"])
            app_state["training_data"] = training_data
            logger.info("Quick predict: auto-prepared training data (scaler + encoders)")
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Data preparation failed: {str(e)}"
            )

    # ── Step 4: Check saved model exists ──
    model_path = SAVED_MODELS_DIR / f"{model_name}.joblib"

    if not model_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Saved model '{model_name}' not found at {model_path}. "
                   f"Please train models at least once using the Training page."
        )

    # ── Step 5: Predict using the saved model ──
    try:
        training_data = app_state["training_data"]

        prediction_result = predict_single_customer(
            customer_data=request.customer_data,
            model_name=model_name,
            scaler=training_data["scaler"],
            encoders=training_data["encoders"],
            feature_names=training_data["feature_names"],
            numeric_cols=training_data["numeric_cols"],
        )

        # Add a flag indicating this was a quick prediction
        prediction_result["quick_predict"] = True

        return prediction_result

    except Exception as e:
        logger.error(f"Quick prediction failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Quick prediction failed: {str(e)}")


@router.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "dataset_loaded": app_state["raw_df"] is not None,
        "dataset_cleaned": app_state["cleaned_df"] is not None,
        "models_trained": app_state["model_results"] is not None,
    }
