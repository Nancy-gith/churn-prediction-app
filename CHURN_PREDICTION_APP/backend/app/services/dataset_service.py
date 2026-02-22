"""
Dataset service — handles loading the default Kaggle dataset
and user-uploaded CSV files.
"""
import pandas as pd
import logging
from pathlib import Path
from app.config import DEFAULT_DATASET_PATH, DATA_DIR

logger = logging.getLogger(__name__)


def generate_default_dataset() -> pd.DataFrame:
    """
    Generate a synthetic but realistic telco churn dataset.
    This serves as the default when no file is uploaded.
    Modeled after the IBM Telco Customer Churn dataset.
    """
    import numpy as np

    np.random.seed(42)
    n = 7043  # Same size as IBM dataset

    # ── Generate customer IDs ──
    customer_ids = [f"{i:04d}-{''.join(np.random.choice(list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 5))}" for i in range(n)]

    # ── Demographics ──
    gender = np.random.choice(["Male", "Female"], n)
    senior_citizen = np.random.choice([0, 1], n, p=[0.84, 0.16])
    partner = np.random.choice(["Yes", "No"], n, p=[0.48, 0.52])
    dependents = np.random.choice(["Yes", "No"], n, p=[0.30, 0.70])

    # ── Services ──
    tenure = np.random.exponential(scale=32, size=n).astype(int).clip(1, 72)
    phone_service = np.random.choice(["Yes", "No"], n, p=[0.90, 0.10])
    multiple_lines = np.where(
        phone_service == "No", "No phone service",
        np.random.choice(["Yes", "No"], n, p=[0.42, 0.58])
    )

    internet_service = np.random.choice(
        ["DSL", "Fiber optic", "No"], n, p=[0.34, 0.44, 0.22]
    )

    def internet_dependent(internet_service, yes_prob=0.30):
        return np.where(
            internet_service == "No", "No internet service",
            np.random.choice(["Yes", "No"], n, p=[yes_prob, 1 - yes_prob])
        )

    online_security = internet_dependent(internet_service, 0.29)
    online_backup = internet_dependent(internet_service, 0.34)
    device_protection = internet_dependent(internet_service, 0.34)
    tech_support = internet_dependent(internet_service, 0.29)
    streaming_tv = internet_dependent(internet_service, 0.38)
    streaming_movies = internet_dependent(internet_service, 0.39)

    # ── Contract & Billing ──
    contract = np.random.choice(
        ["Month-to-month", "One year", "Two year"], n, p=[0.55, 0.21, 0.24]
    )
    paperless_billing = np.random.choice(["Yes", "No"], n, p=[0.59, 0.41])
    payment_method = np.random.choice(
        ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"],
        n, p=[0.34, 0.23, 0.22, 0.21]
    )

    # ── Charges ──
    monthly_base = np.where(internet_service == "No", 20, np.where(internet_service == "DSL", 45, 70))
    monthly_charges = (monthly_base + np.random.normal(0, 10, n)).clip(18, 120).round(2)
    total_charges = (monthly_charges * tenure + np.random.normal(0, 50, n)).clip(18, 9000).round(2)

    # ── Support Calls ──
    support_calls = np.random.poisson(lam=1.5, size=n).clip(0, 9)

    # ── Churn (target) — correlated with features ──
    churn_prob = (
        0.05
        + 0.25 * (contract == "Month-to-month")
        + 0.15 * (internet_service == "Fiber optic")
        + 0.10 * (payment_method == "Electronic check")
        + 0.08 * (paperless_billing == "Yes")
        - 0.15 * (tenure > 24)
        - 0.10 * (online_security == "Yes")
        + 0.05 * (support_calls > 3)
        + 0.03 * (monthly_charges > 70)
    ).clip(0.02, 0.95)
    churn = np.where(np.random.random(n) < churn_prob, "Yes", "No")

    df = pd.DataFrame({
        "customerID": customer_ids,
        "gender": gender,
        "SeniorCitizen": senior_citizen,
        "Partner": partner,
        "Dependents": dependents,
        "tenure": tenure,
        "PhoneService": phone_service,
        "MultipleLines": multiple_lines,
        "InternetService": internet_service,
        "OnlineSecurity": online_security,
        "OnlineBackup": online_backup,
        "DeviceProtection": device_protection,
        "TechSupport": tech_support,
        "StreamingTV": streaming_tv,
        "StreamingMovies": streaming_movies,
        "Contract": contract,
        "PaperlessBilling": paperless_billing,
        "PaymentMethod": payment_method,
        "MonthlyCharges": monthly_charges,
        "TotalCharges": total_charges,
        "SupportCalls": support_calls,
        "Churn": churn,
    })

    # Inject realistic data issues (like the real IBM dataset)
    # 1) TotalCharges has some whitespace strings for new customers
    new_customer_mask = tenure <= 1
    whitespace_indices = df[new_customer_mask].sample(
        min(11, new_customer_mask.sum()), random_state=42
    ).index
    df.loc[whitespace_indices, "TotalCharges"] = " "

    # 2) Make TotalCharges a string column (like the original)
    df["TotalCharges"] = df["TotalCharges"].astype(str)

    # Save to disk
    df.to_csv(DEFAULT_DATASET_PATH, index=False)
    logger.info(f"Generated default dataset with {len(df)} rows at {DEFAULT_DATASET_PATH}")

    return df


def load_default_dataset() -> pd.DataFrame:
    """Load the default dataset, generating it if necessary."""
    if DEFAULT_DATASET_PATH.exists():
        logger.info(f"Loading existing dataset from {DEFAULT_DATASET_PATH}")
        return pd.read_csv(DEFAULT_DATASET_PATH)
    else:
        logger.info("Default dataset not found. Generating synthetic dataset...")
        return generate_default_dataset()


def load_uploaded_dataset(file_path: str) -> pd.DataFrame:
    """Load a user-uploaded CSV file."""
    df = pd.read_csv(file_path)
    logger.info(f"Loaded uploaded dataset with {len(df)} rows, {len(df.columns)} columns")
    return df


def get_dataset_preview(df: pd.DataFrame, n_rows: int = 20) -> dict:
    """
    Return a JSON-serializable preview of the dataset.
    Includes first N rows, shape, column names, and dtypes.
    """
    return {
        "shape": {"rows": df.shape[0], "columns": df.shape[1]},
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "head": df.head(n_rows).fillna("").to_dict(orient="records"),
        "missing_values": df.isnull().sum().to_dict(),
        "sample_values": {col: df[col].dropna().unique()[:5].tolist() for col in df.columns},
    }
