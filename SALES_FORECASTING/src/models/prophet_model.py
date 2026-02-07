"""
Prophet Model
Facebook's Prophet forecasting implementation.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
import warnings
from .base_model import BaseForecaster

warnings.filterwarnings('ignore')


class ProphetForecaster(BaseForecaster):
    """
    Prophet forecaster - Facebook's robust time series forecasting tool.
    Handles seasonality, trends, and holidays automatically.
    """
    
    def __init__(self, yearly_seasonality: bool = True, weekly_seasonality: bool = True):
        """
        Initialize Prophet forecaster.
        
        Args:
            yearly_seasonality: Whether to include yearly seasonality
            weekly_seasonality: Whether to include weekly seasonality
        """
        super().__init__("Prophet")
        self.yearly_seasonality = yearly_seasonality
        self.weekly_seasonality = weekly_seasonality
        self.prophet_model = None
        self.last_date = None
        self.prophet_df = None
    
    def fit(self, data: pd.DataFrame, date_col: str, value_col: str) -> None:
        """Fit Prophet model to the data."""
        from prophet import Prophet
        
        is_valid, msg = self.validate_data(data, 60)
        if not is_valid:
            raise ValueError(msg)
        
        self.training_data = data.copy()
        self.date_col = date_col
        self.value_col = value_col
        self.last_date = data[date_col].max()
        
        # Prophet requires 'ds' and 'y' columns
        self.prophet_df = pd.DataFrame({
            'ds': data[date_col],
            'y': data[value_col]
        })
        
        # Initialize and fit Prophet
        self.prophet_model = Prophet(
            yearly_seasonality=self.yearly_seasonality,
            weekly_seasonality=self.weekly_seasonality,
            daily_seasonality=False,
            seasonality_mode='multiplicative'
        )
        self.prophet_model.fit(self.prophet_df)
        self.is_fitted = True
    
    def predict(self, periods: int) -> pd.DataFrame:
        """Generate forecasts using Prophet."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction.")
        
        # Create future dataframe
        future = self.prophet_model.make_future_dataframe(periods=periods)
        
        # Generate forecast
        forecast = self.prophet_model.predict(future)
        
        # Get only future predictions
        future_forecast = forecast[forecast['ds'] > self.last_date].copy()
        
        return pd.DataFrame({
            'Date': future_forecast['ds'].values,
            'Forecast': future_forecast['yhat'].values,
            'Lower_CI': future_forecast['yhat_lower'].values,
            'Upper_CI': future_forecast['yhat_upper'].values,
            'Model': self.name
        })
    
    def get_fitted_values(self) -> Optional[np.ndarray]:
        """Get in-sample fitted values."""
        if self.prophet_model is None or self.prophet_df is None:
            return None
        
        forecast = self.prophet_model.predict(self.prophet_df)
        return forecast['yhat'].values
    
    def get_description(self) -> Dict[str, str]:
        """Get model description."""
        return {
            "brief": "Facebook's robust forecasting tool designed for business time series.",
            "how_it_works": "Decomposes time series into:\n"
                          "• Trend: Long-term direction\n"
                          "• Seasonality: Weekly and yearly patterns\n"
                          "• Holidays: Special events (optional)\n"
                          "Uses additive/multiplicative regression.",
            "when_to_use": "Excellent for business data with multiple seasonalities. "
                          "Great when you have yearly patterns, weekly patterns, or both.",
            "strengths": "• Automatic seasonality detection\n"
                        "• Handles missing data well\n"
                        "• Intuitive parameters\n"
                        "• Provides uncertainty intervals\n"
                        "• Can incorporate holidays",
            "limitations": "• Can overfit on short time series\n"
                          "• Slower than simple methods\n"
                          "• May not capture sudden changes\n"
                          "• Requires at least 2 periods of seasonality data"
        }
