"""
ARIMA Model
AutoRegressive Integrated Moving Average implementation.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
import warnings
from .base_model import BaseForecaster

# Suppress convergence warnings
warnings.filterwarnings('ignore')


class ARIMAForecaster(BaseForecaster):
    """
    ARIMA (AutoRegressive Integrated Moving Average) forecaster.
    Combines autoregression, differencing, and moving average components.
    """
    
    def __init__(self, order: Tuple[int, int, int] = None, auto_select: bool = True):
        """
        Initialize ARIMA forecaster.
        
        Args:
            order: (p, d, q) parameters. If None and auto_select=True, will auto-select.
            auto_select: Whether to automatically select best parameters
        """
        super().__init__("ARIMA")
        self.order = order
        self.auto_select = auto_select
        self.fitted_model = None
        self.last_date = None
    
    def _auto_select_order(self, data: np.ndarray) -> Tuple[int, int, int]:
        """
        Auto-select ARIMA parameters using AIC criterion.
        Simplified grid search over common parameter ranges.
        """
        from statsmodels.tsa.arima.model import ARIMA
        
        best_aic = float('inf')
        best_order = (1, 1, 1)  # Default
        
        # Simplified search space
        p_values = [0, 1, 2]
        d_values = [0, 1]
        q_values = [0, 1, 2]
        
        for p in p_values:
            for d in d_values:
                for q in q_values:
                    try:
                        model = ARIMA(data, order=(p, d, q))
                        fitted = model.fit()
                        if fitted.aic < best_aic:
                            best_aic = fitted.aic
                            best_order = (p, d, q)
                    except:
                        continue
        
        return best_order
    
    def fit(self, data: pd.DataFrame, date_col: str, value_col: str) -> None:
        """Fit ARIMA model to the data."""
        from statsmodels.tsa.arima.model import ARIMA
        
        is_valid, msg = self.validate_data(data, 30)
        if not is_valid:
            raise ValueError(msg)
        
        self.training_data = data.copy()
        self.date_col = date_col
        self.value_col = value_col
        self.last_date = data[date_col].max()
        
        values = data[value_col].values
        
        # Auto-select order if needed
        if self.order is None and self.auto_select:
            self.order = self._auto_select_order(values)
        elif self.order is None:
            self.order = (1, 1, 1)
        
        # Fit the model
        model = ARIMA(values, order=self.order)
        self.fitted_model = model.fit()
        self.is_fitted = True
    
    def predict(self, periods: int) -> pd.DataFrame:
        """Generate forecasts using ARIMA."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction.")
        
        # Get forecast with confidence intervals
        forecast_result = self.fitted_model.get_forecast(steps=periods)
        forecast_mean = forecast_result.predicted_mean
        conf_int = forecast_result.conf_int(alpha=0.05)
        
        future_dates = pd.date_range(
            start=self.last_date + pd.Timedelta(days=1),
            periods=periods,
            freq='D'
        )
        
        return pd.DataFrame({
            'Date': future_dates,
            'Forecast': forecast_mean.values,
            'Lower_CI': conf_int.iloc[:, 0].values,
            'Upper_CI': conf_int.iloc[:, 1].values,
            'Model': self.name
        })
    
    def get_fitted_values(self) -> Optional[np.ndarray]:
        """Get in-sample fitted values."""
        if self.fitted_model is None:
            return None
        return self.fitted_model.fittedvalues
    
    def get_description(self) -> Dict[str, str]:
        """Get model description."""
        order_str = f"({self.order[0]}, {self.order[1]}, {self.order[2]})" if self.order else "(auto)"
        return {
            "brief": "Statistical model combining autoregression, differencing, and moving average.",
            "how_it_works": f"ARIMA{order_str} uses:\n"
                          f"• AR({self.order[0] if self.order else '?'}): Past values predict future\n"
                          f"• I({self.order[1] if self.order else '?'}): Differencing and for stationarity\n"
                          f"• MA({self.order[2] if self.order else '?'}): Past errors predict future",
            "when_to_use": "Best for data with trends but without strong seasonality. "
                          "Standard choice for many business forecasting tasks.",
            "strengths": "• Handles trends well\n"
                        "• Provides confidence intervals\n"
                        "• Well-established statistical foundation\n"
                        "• Automatic parameter selection available",
            "limitations": "• Assumes linear relationships\n"
                          "• Requires stationary data (after differencing)\n"
                          "• May not capture complex seasonality\n"
                          "• Can be slow for large datasets"
        }
