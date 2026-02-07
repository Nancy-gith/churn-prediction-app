"""
Base Model Module
Abstract base class for all forecasting models.
"""

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple


class BaseForecaster(ABC):
    """
    Abstract base class for time series forecasting models.
    All forecasting models should inherit from this class.
    """
    
    def __init__(self, name: str):
        """
        Initialize the forecaster.
        
        Args:
            name: Display name of the model
        """
        self.name = name
        self.is_fitted = False
        self.training_data = None
        self.model = None
    
    @abstractmethod
    def fit(self, data: pd.DataFrame, date_col: str, value_col: str) -> None:
        """
        Fit the model to training data.
        
        Args:
            data: Training DataFrame
            date_col: Name of date column
            value_col: Name of value column
        """
        pass
    
    @abstractmethod
    def predict(self, periods: int) -> pd.DataFrame:
        """
        Generate forecasts for future periods.
        
        Args:
            periods: Number of periods to forecast
        
        Returns:
            DataFrame with date, forecast, and optional confidence intervals
        """
        pass
    
    @abstractmethod
    def get_description(self) -> Dict[str, str]:
        """
        Get model description for educational component.
        
        Returns:
            Dictionary with 'brief', 'how_it_works', 'when_to_use', 'strengths', 'limitations'
        """
        pass
    
    def get_fitted_values(self) -> Optional[np.ndarray]:
        """
        Get fitted values (in-sample predictions) if available.
        
        Returns:
            Array of fitted values or None
        """
        return None
    
    def validate_data(self, data: pd.DataFrame, min_points: int) -> Tuple[bool, str]:
        """
        Validate that data has sufficient points for forecasting.
        
        Args:
            data: Input DataFrame
            min_points: Minimum required data points
        
        Returns:
            Tuple of (is_valid, message)
        """
        if len(data) < min_points:
            return False, f"Insufficient data. Need at least {min_points} points, got {len(data)}."
        return True, "Data validation passed."
