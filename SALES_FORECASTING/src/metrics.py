"""
Metrics Module
Functions for calculating forecast accuracy metrics.
"""

import numpy as np
import pandas as pd
from typing import Dict


def calculate_mae(actual: np.ndarray, predicted: np.ndarray) -> float:
    """
    Calculate Mean Absolute Error.
    
    MAE = (1/n) * Σ|actual - predicted|
    
    Interpretation: Average magnitude of errors in the same units as data.
    Lower is better.
    """
    return np.mean(np.abs(actual - predicted))


def calculate_rmse(actual: np.ndarray, predicted: np.ndarray) -> float:
    """
    Calculate Root Mean Square Error.
    
    RMSE = √[(1/n) * Σ(actual - predicted)²]
    
    Interpretation: Standard deviation of prediction errors.
    Penalizes large errors more than MAE. Lower is better.
    """
    return np.sqrt(np.mean((actual - predicted) ** 2))


def calculate_mape(actual: np.ndarray, predicted: np.ndarray) -> float:
    """
    Calculate Mean Absolute Percentage Error.
    
    MAPE = (100/n) * Σ|(actual - predicted) / actual|
    
    Interpretation: Average percentage error.
    Useful for comparing across different scales. Lower is better.
    """
    # Avoid division by zero
    mask = actual != 0
    if not np.any(mask):
        return np.nan
    return np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100


def calculate_all_metrics(actual: np.ndarray, predicted: np.ndarray) -> Dict[str, float]:
    """
    Calculate all accuracy metrics.
    
    Args:
        actual: Array of actual values
        predicted: Array of predicted values
    
    Returns:
        Dictionary with MAE, RMSE, and MAPE
    """
    actual = np.array(actual)
    predicted = np.array(predicted)
    
    return {
        "MAE": round(calculate_mae(actual, predicted), 2),
        "RMSE": round(calculate_rmse(actual, predicted), 2),
        "MAPE": round(calculate_mape(actual, predicted), 2)
    }


def get_best_model(metrics_dict: Dict[str, Dict[str, float]], metric: str = "RMSE") -> str:
    """
    Get the name of the best performing model based on specified metric.
    
    Args:
        metrics_dict: Dictionary of model_name -> metrics
        metric: Metric to use for comparison (MAE, RMSE, or MAPE)
    
    Returns:
        Name of the best model
    """
    best_model = None
    best_value = float('inf')
    
    for model_name, metrics in metrics_dict.items():
        if metrics.get(metric, float('inf')) < best_value:
            best_value = metrics[metric]
            best_model = model_name
    
    return best_model


def format_metrics_table(metrics_dict: Dict[str, Dict[str, float]]) -> pd.DataFrame:
    """
    Format metrics dictionary as a pandas DataFrame for display.
    
    Args:
        metrics_dict: Dictionary of model_name -> metrics
    
    Returns:
        DataFrame with models as rows and metrics as columns
    """
    df = pd.DataFrame(metrics_dict).T
    df.index.name = "Model"
    return df.reset_index()
