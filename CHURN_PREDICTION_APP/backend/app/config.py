"""
Application configuration — centralizes all settings.
Uses environment variables for deployment flexibility.
"""
import os
from pathlib import Path

# ── Paths ─────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SAVED_MODELS_DIR = BASE_DIR / "saved_models"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
SAVED_MODELS_DIR.mkdir(exist_ok=True)

# ── API Settings ──────────────────────────────────────
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("PORT", "8000"))

# ── CORS ──────────────────────────────────────────────
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
).split(",")

# ── Dataset ───────────────────────────────────────────
DEFAULT_DATASET_PATH = DATA_DIR / "telco_churn.csv"

# ── ML Settings ───────────────────────────────────────
TEST_SIZE = 0.2
RANDOM_STATE = 42
SMOTE_RANDOM_STATE = 42
OPTUNA_N_TRIALS = 30  # Number of hyperparameter tuning trials

# ── Column Definitions ────────────────────────────────
# These map to the IBM Telco Churn dataset schema
TARGET_COLUMN = "Churn"
ID_COLUMNS = ["customerID", "CustomerID", "Name", "PhoneNumber", "SIM"]

NUMERIC_COLUMNS = ["tenure", "MonthlyCharges", "TotalCharges", "SupportCalls"]
CATEGORICAL_COLUMNS = [
    "gender", "SeniorCitizen", "Partner", "Dependents",
    "PhoneService", "MultipleLines", "InternetService",
    "OnlineSecurity", "OnlineBackup", "DeviceProtection",
    "TechSupport", "StreamingTV", "StreamingMovies",
    "Contract", "PaperlessBilling", "PaymentMethod",
    "ContractType"
]

BINARY_COLUMNS = [
    "gender", "SeniorCitizen", "Partner", "Dependents",
    "PhoneService", "PaperlessBilling"
]
