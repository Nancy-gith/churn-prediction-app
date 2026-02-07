"""
Moving Average Models
Simple Moving Average (SMA) and Weighted Moving Average (WMA) implementations.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from .base_model import BaseForecaster


class SimpleMovingAverage(BaseForecaster):
    """
    Simple Moving Average forecaster.
    Calculates the average of the last n observations.
    """
    
    def __init__(self, window: int = 7):
        """
        Initialize SMA forecaster.
        
        Args:
            window: Number of periods to average
        """
        super().__init__("Simple Moving Average")
        self.window = window
        self.last_values = None
        self.last_date = None
    
    def fit(self, data: pd.DataFrame, date_col: str, value_col: str) -> None:
        """Fit the model by storing the training data."""
        is_valid, msg = self.validate_data(data, self.window)
        if not is_valid:
            raise ValueError(msg)
        
        self.training_data = data.copy()
        self.date_col = date_col
        self.value_col = value_col
        self.last_values = data[value_col].tail(self.window).values
        self.last_date = data[date_col].max()
        self.is_fitted = True
    
    def predict(self, periods: int) -> pd.DataFrame:
        """Generate forecasts using simple moving average."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction.")
        
        forecasts = []
        values = list(self.last_values)
        
        # Generate future dates
        future_dates = pd.date_range(
            start=self.last_date + pd.Timedelta(days=1),
            periods=periods,
            freq='D'
        )
        
        for date in future_dates:
            # Calculate SMA
            forecast = np.mean(values[-self.window:])
            forecasts.append({
                'Date': date,
                'Forecast': forecast,
                'Model': self.name
            })
            # Add forecast to values for next prediction
            values.append(forecast)
        
        return pd.DataFrame(forecasts)
    
    def get_fitted_values(self) -> Optional[np.ndarray]:
        """Get rolling average of training data."""
        if self.training_data is None:
            return None
        return self.training_data[self.value_col].rolling(window=self.window).mean().values
    
    def get_description(self) -> Dict[str, str]:
        """Get model description."""
        return {
            "brief": "Averages the last N observations to predict future values.",
            "how_it_works": f"Takes the mean of the last {self.window} data points. "
                          "Each new forecast becomes part of the window for subsequent predictions.",
            "when_to_use": "Best for stable data without strong trends or seasonality. "
                          "Good baseline model for comparison.",
            "strengths": "• Simple and easy to understand\n"
                        "• No complex parameters to tune\n"
                        "• Works well for stable patterns\n"
                        "• Fast computation",
            "limitations": "• Lags behind trends\n"
                          "• Gives equal weight to all observations in window\n"
                          "• Cannot capture seasonality\n"
                          "• No confidence intervals"
        }


class WeightedMovingAverage(BaseForecaster):
    """
    Weighted Moving Average forecaster.
    More recent observations receive higher weights.
    """
    
    def __init__(self, window: int = 7):
        """
        Initialize WMA forecaster.
        
        Args:
            window: Number of periods to consider
        """
        super().__init__("Weighted Moving Average")
        self.window = window
        self.weights = self._create_weights(window)
        self.last_values = None
        self.last_date = None
    
    def _create_weights(self, n: int) -> np.ndarray:
        """Create linearly increasing weights that sum to 1."""
        weights = np.arange(1, n + 1, dtype=float)
        return weights / weights.sum()
    
    def fit(self, data: pd.DataFrame, date_col: str, value_col: str) -> None:
        """Fit the model by storing the training data."""
        is_valid, msg = self.validate_data(data, self.window)
        if not is_valid:
            raise ValueError(msg)
        
        self.training_data = data.copy()
        self.date_col = date_col
        self.value_col = value_col
        self.last_values = data[value_col].tail(self.window).values
        self.last_date = data[date_col].max()
        self.is_fitted = True
    
    def predict(self, periods: int) -> pd.DataFrame:
        """Generate forecasts using weighted moving average."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction.")
        
        forecasts = []
        values = list(self.last_values)
        
        future_dates = pd.date_range(
            start=self.last_date + pd.Timedelta(days=1),
            periods=periods,
            freq='D'
        )
        
        for date in future_dates:
            # Calculate WMA
            recent_values = np.array(values[-self.window:])
            forecast = np.sum(recent_values * self.weights)
            forecasts.append({
                'Date': date,
                'Forecast': forecast,
                'Model': self.name
            })
            values.append(forecast)
        
        return pd.DataFrame(forecasts)
    
    def get_fitted_values(self) -> Optional[np.ndarray]:
        """Get weighted rolling average of training data."""
        if self.training_data is None:
            return None
        
        values = self.training_data[self.value_col].values
        fitted = np.full(len(values), np.nan)
        
        for i in range(self.window - 1, len(values)):
            window_values = values[i - self.window + 1:i + 1]
            fitted[i] = np.sum(window_values * self.weights)
        
        return fitted
    
    def get_description(self) -> Dict[str, str]:
        """Get model description."""
        return {
            "brief": "Like SMA, but gives more weight to recent observations.",
            "how_it_works": f"Uses {self.window} periods with linearly increasing weights. "
                          "The most recent observation has the highest weight.",
            "when_to_use": "When recent data is more important than older data. "
                          "Better than SMA when data has gradual trends.",
            "strengths": "• More responsive to recent changes\n"
                        "• Still relatively simple\n"
                        "• Better trend following than SMA\n"
                        "• Customizable weights",
            "limitations": "• Still lags behind sharp changes\n"
                          "• Cannot capture seasonality\n"
                          "• No confidence intervals\n"
                          "• Weight selection can be arbitrary"
        }
