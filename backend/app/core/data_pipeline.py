"""
Data Pipeline — cleaning, preprocessing, and feature engineering.

This module handles ALL data transformations from raw CSV to ML-ready features.
Every decision is documented with rationale.
"""
import pandas as pd
import numpy as np
import logging
from typing import Tuple, Dict, Any, List, Optional
from sklearn.preprocessing import StandardScaler, LabelEncoder
from imblearn.over_sampling import SMOTE
from app.config import (
    TARGET_COLUMN, ID_COLUMNS, RANDOM_STATE, SMOTE_RANDOM_STATE
)

logger = logging.getLogger(__name__)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. DATA CLEANING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_cleaning_report(df_raw: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate a comprehensive 'before' report of data quality issues.
    This is sent to the frontend BEFORE cleaning so users see what was fixed.
    """
    report = {
        "total_rows": len(df_raw),
        "total_columns": len(df_raw.columns),
        "columns": list(df_raw.columns),
        "dtypes_before": {col: str(dtype) for col, dtype in df_raw.dtypes.items()},
        "missing_values": {},
        "data_type_issues": [],
        "outlier_info": {},
        "duplicate_rows": int(df_raw.duplicated().sum()),
    }

    # Check missing values per column
    for col in df_raw.columns:
        missing = int(df_raw[col].isnull().sum())
        # Also check for whitespace-only strings (common in TotalCharges)
        if df_raw[col].dtype == object:
            whitespace_count = int((df_raw[col].str.strip() == "").sum())
            missing += whitespace_count
        if missing > 0:
            report["missing_values"][col] = {
                "count": missing,
                "percentage": round(missing / len(df_raw) * 100, 2)
            }

    # Check data type issues
    if "TotalCharges" in df_raw.columns:
        if df_raw["TotalCharges"].dtype == object:
            report["data_type_issues"].append({
                "column": "TotalCharges",
                "current_type": "string/object",
                "expected_type": "float64",
                "reason": "Contains whitespace strings for new customers with 0 tenure"
            })

    return report


def clean_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Master cleaning function. Returns cleaned DataFrame and a report
    of all transformations applied.

    Steps:
    1. Drop ID columns (not predictive)
    2. Fix data types (TotalCharges string → float)
    3. Handle missing values
    4. Remove duplicates
    5. Detect and treat outliers (Winsorization)
    """
    report_before = get_cleaning_report(df)
    df_clean = df.copy()
    transformations = []

    # ── Step 1: Drop ID / non-predictive columns ──
    cols_to_drop = [c for c in ID_COLUMNS if c in df_clean.columns]
    if cols_to_drop:
        df_clean = df_clean.drop(columns=cols_to_drop)
        transformations.append({
            "step": "Drop ID columns",
            "columns": cols_to_drop,
            "reason": "IDs and personal info are not predictive features"
        })

    # ── Step 2: Fix TotalCharges data type ──
    if "TotalCharges" in df_clean.columns:
        # Replace whitespace strings with NaN, then convert
        df_clean["TotalCharges"] = df_clean["TotalCharges"].replace(r"^\s*$", np.nan, regex=True)
        df_clean["TotalCharges"] = pd.to_numeric(df_clean["TotalCharges"], errors="coerce")
        transformations.append({
            "step": "Fix TotalCharges type",
            "action": "Converted from string to float64",
            "reason": "IBM dataset stores TotalCharges as string; whitespace for new customers"
        })

    # ── Step 3: Handle missing values ──
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
    if TARGET_COLUMN in numeric_cols:
        numeric_cols.remove(TARGET_COLUMN)

    cat_cols = df_clean.select_dtypes(include=["object"]).columns.tolist()
    if TARGET_COLUMN in cat_cols:
        cat_cols.remove(TARGET_COLUMN)

    # Numeric: fill with median
    for col in numeric_cols:
        missing = df_clean[col].isnull().sum()
        if missing > 0:
            median_val = df_clean[col].median()
            df_clean[col] = df_clean[col].fillna(median_val)
            transformations.append({
                "step": f"Impute {col}",
                "action": f"Filled {missing} missing values with median ({median_val:.2f})",
                "reason": "Median is robust to outliers, preserves central tendency"
            })

    # Categorical: fill with mode
    for col in cat_cols:
        missing = df_clean[col].isnull().sum()
        if missing > 0:
            mode_val = df_clean[col].mode()[0]
            df_clean[col] = df_clean[col].fillna(mode_val)
            transformations.append({
                "step": f"Impute {col}",
                "action": f"Filled {missing} missing values with mode ('{mode_val}')",
                "reason": "Mode preserves the most common category distribution"
            })

    # ── Step 4: Remove duplicates ──
    dup_count = df_clean.duplicated().sum()
    if dup_count > 0:
        df_clean = df_clean.drop_duplicates()
        transformations.append({
            "step": "Remove duplicates",
            "action": f"Removed {dup_count} duplicate rows",
            "reason": "Duplicates inflate training data artificially"
        })

    # ── Step 5: Outlier detection & treatment (Winsorization) ──
    outlier_info = {}
    for col in numeric_cols:
        Q1 = df_clean[col].quantile(0.25)
        Q3 = df_clean[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outliers_below = int((df_clean[col] < lower_bound).sum())
        outliers_above = int((df_clean[col] > upper_bound).sum())
        total_outliers = outliers_below + outliers_above

        if total_outliers > 0:
            df_clean[col] = df_clean[col].clip(lower_bound, upper_bound)
            outlier_info[col] = {
                "outliers_found": total_outliers,
                "lower_bound": round(float(lower_bound), 2),
                "upper_bound": round(float(upper_bound), 2),
                "treatment": "Winsorized (capped at IQR boundaries)"
            }
            transformations.append({
                "step": f"Outlier treatment: {col}",
                "action": f"Capped {total_outliers} outliers at [{lower_bound:.2f}, {upper_bound:.2f}]",
                "reason": "Winsorization preserves data points while reducing extreme influence"
            })

    # ── Step 6: Encode target variable ──
    if TARGET_COLUMN in df_clean.columns:
        if df_clean[TARGET_COLUMN].dtype == object:
            df_clean[TARGET_COLUMN] = df_clean[TARGET_COLUMN].map({"Yes": 1, "No": 0})
            transformations.append({
                "step": "Encode target",
                "action": "Mapped Churn: Yes→1, No→0",
                "reason": "Binary classification requires numeric target"
            })

    report_after = get_cleaning_report(df_clean)

    cleaning_report = {
        "before": report_before,
        "after": report_after,
        "transformations": transformations,
        "outlier_details": outlier_info,
        "shape_before": {"rows": report_before["total_rows"], "columns": report_before["total_columns"]},
        "shape_after": {"rows": len(df_clean), "columns": len(df_clean.columns)},
    }

    return df_clean, cleaning_report


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. FEATURE ENGINEERING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def encode_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any], dict]:
    """
    Encode categorical features for ML models.

    Strategy:
    - Binary columns (2 unique values): LabelEncoder (0/1)
    - Multi-category columns (3+ unique values): One-Hot Encoding
    - Why not target encoding? Risk of data leakage without proper CV folds.

    Returns:
        df_encoded: Encoded DataFrame
        encoding_info: Dict with encoding details for frontend display
        encoders: Dict of fitted encoders for prediction-time use
    """
    df_enc = df.copy()
    encoding_info = {"binary": [], "one_hot": []}
    encoders = {"label_encoders": {}, "one_hot_columns": []}

    cat_cols = df_enc.select_dtypes(include=["object"]).columns.tolist()
    if TARGET_COLUMN in cat_cols:
        cat_cols.remove(TARGET_COLUMN)

    for col in cat_cols:
        unique_count = df_enc[col].nunique()

        if unique_count <= 2:
            # Binary → Label Encoding
            le = LabelEncoder()
            df_enc[col] = le.fit_transform(df_enc[col])
            encoders["label_encoders"][col] = le
            encoding_info["binary"].append({
                "column": col,
                "mapping": dict(zip(le.classes_, le.transform(le.classes_).tolist()))
            })
        else:
            # Multi-category → One-Hot Encoding
            dummies = pd.get_dummies(df_enc[col], prefix=col, drop_first=True, dtype=int)
            df_enc = pd.concat([df_enc, dummies], axis=1)
            df_enc = df_enc.drop(columns=[col])
            encoders["one_hot_columns"].append({
                "original": col,
                "new_columns": list(dummies.columns)
            })
            encoding_info["one_hot"].append({
                "column": col,
                "categories": dummies.columns.tolist()
            })

    return df_enc, encoding_info, encoders


def scale_features(
    X_train: pd.DataFrame, X_test: pd.DataFrame,
    numeric_cols: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, pd.DataFrame, StandardScaler]:
    """
    Apply StandardScaler to numeric features.

    Why StandardScaler?
    - Centers data (mean=0, std=1)
    - Required by Logistic Regression (gradient descent converges faster)
    - Required by Neural Networks (prevents vanishing/exploding gradients)
    - Tree-based models DON'T need this, but it doesn't hurt them

    CRITICAL: Fit on train, transform on both train and test.
    """
    if numeric_cols is None:
        numeric_cols = X_train.select_dtypes(include=[np.number]).columns.tolist()

    scaler = StandardScaler()

    X_train_scaled = X_train.copy()
    X_test_scaled = X_test.copy()

    X_train_scaled[numeric_cols] = scaler.fit_transform(X_train[numeric_cols])
    X_test_scaled[numeric_cols] = scaler.transform(X_test[numeric_cols])

    return X_train_scaled, X_test_scaled, scaler


def apply_smote(
    X_train: pd.DataFrame, y_train: pd.Series
) -> Tuple[pd.DataFrame, pd.Series, Dict[str, Any]]:
    """
    Apply SMOTE to handle class imbalance.

    Why SMOTE?
    - Creates synthetic minority samples via interpolation (not duplication)
    - Better generalization than random oversampling
    - Preserves the boundary decision region

    CRITICAL: Only apply to training data. NEVER SMOTE test data.
    """
    class_counts_before = y_train.value_counts().to_dict()

    smote = SMOTE(random_state=SMOTE_RANDOM_STATE)
    X_resampled, y_resampled = smote.fit_resample(X_train, y_train)

    X_resampled = pd.DataFrame(X_resampled, columns=X_train.columns)
    y_resampled = pd.Series(y_resampled, name=y_train.name)

    class_counts_after = y_resampled.value_counts().to_dict()

    smote_info = {
        "applied": True,
        "class_distribution_before": {str(k): int(v) for k, v in class_counts_before.items()},
        "class_distribution_after": {str(k): int(v) for k, v in class_counts_after.items()},
        "samples_added": int(len(y_resampled) - len(y_train)),
        "technique": "SMOTE (Synthetic Minority Over-sampling Technique)",
        "rationale": "Creates synthetic interpolated samples for minority class"
    }

    logger.info(f"SMOTE: {len(y_train)} → {len(y_resampled)} samples")
    return X_resampled, y_resampled, smote_info


def prepare_data_for_training(
    df_clean: pd.DataFrame
) -> Dict[str, Any]:
    """
    Full pipeline: encode → split → scale → SMOTE → return everything needed.

    Returns a dict with X_train, X_test, y_train, y_test, plus all
    fitted transformers for prediction-time use.
    """
    from sklearn.model_selection import train_test_split
    from app.config import TEST_SIZE

    if TARGET_COLUMN not in df_clean.columns:
        raise ValueError(f"Target column '{TARGET_COLUMN}' not found in dataset")

    # Separate features and target
    X = df_clean.drop(columns=[TARGET_COLUMN])
    y = df_clean[TARGET_COLUMN]

    # Encode categorical features
    X_encoded, encoding_info, encoders = encode_features(X)

    # Store feature names for later use
    feature_names = list(X_encoded.columns)

    # Train/test split (stratified to preserve class ratio)
    X_train, X_test, y_train, y_test = train_test_split(
        X_encoded, y, test_size=TEST_SIZE,
        random_state=RANDOM_STATE, stratify=y
    )

    # Scale features
    numeric_cols = X_train.select_dtypes(include=[np.number]).columns.tolist()
    X_train_scaled, X_test_scaled, scaler = scale_features(X_train, X_test, numeric_cols)

    # Apply SMOTE to training data only
    X_train_final, y_train_final, smote_info = apply_smote(X_train_scaled, y_train)

    return {
        "X_train": X_train_final,
        "X_test": X_test_scaled,
        "y_train": y_train_final,
        "y_test": y_test,
        "scaler": scaler,
        "encoders": encoders,
        "encoding_info": encoding_info,
        "smote_info": smote_info,
        "feature_names": feature_names,
        "numeric_cols": numeric_cols,
    }
