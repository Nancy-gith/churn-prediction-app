"""
FastAPI Application Entry Point.

This is the main file that creates and configures the FastAPI app.
Run with: uvicorn app.main:app --reload
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import ALLOWED_ORIGINS, API_HOST, API_PORT
from app.api.routes import router

# ── Configure logging ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Create FastAPI app ──
app = FastAPI(
    title="Telecom Churn Prediction API",
    description=(
        "Production-grade API for predicting telecom customer churn. "
        "Supports data upload, cleaning, EDA, model training (3 gradient boosting models), "
        "evaluation, SHAP explanations, and individual predictions."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS Middleware ──
# Allows the React frontend (localhost:5173 in dev) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include API routes ──
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "app": "Telecom Churn Prediction API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
        "endpoints": [
            "POST /api/upload",
            "GET  /api/load-default",
            "GET  /api/dataset-preview",
            "POST /api/clean",
            "GET  /api/cleaning-report",
            "GET  /api/eda",
            "POST /api/train",
            "GET  /api/evaluation",
            "GET  /api/shap/{model}",
            "POST /api/predict",
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=API_HOST, port=API_PORT, reload=True)
