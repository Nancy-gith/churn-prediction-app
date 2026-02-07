"""
XGBoost Model
Gradient Boosting based time series forecasting.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from .base_model import BaseForecaster


class XGBoostForecaster(BaseForecaster):
    """
    XGBoost forecaster using gradient boosting with time-based features.
    Captures complex non-linear patterns in the data.
    """
    
    def __init__(self, n_lags: int = 7, n_estimators: int = 100):
        """
        Initialize XGBoost forecaster.
        
        Args:
            n_lags: Number of lag features to create
            n_estimators: Number of boosting rounds
        """
        super().__init__("XGBoost")
        self.n_lags = n_lags
        self.n_estimators = n_estimators
        self.xgb_model = None
        self.last_date = None
        self.last_values = None
    
    def _create_features(self, data: pd.DataFrame, date_col: str, value_col: str) -> pd.DataFrame:
        """Create time-based and lag features for XGBoost."""
        df = data.copy()
        
        # Time-based features
        df['dayofweek'] = pd.to_datetime(df[date_col]).dt.dayofweek
        df['dayofmonth'] = pd.to_datetime(df[date_col]).dt.day
        df['month'] = pd.to_datetime(df[date_col]).dt.month
        df['weekofyear'] = pd.to_datetime(df[date_col]).dt.isocalendar().week.astype(int)
        df['is_weekend'] = (df['dayofweek'] >= 5).astype(int)
        
        # Lag features
        for lag in range(1, self.n_lags + 1):
            df[f'lag_{lag}'] = df[value_col].shift(lag)
        
        # Rolling statistics
        df['rolling_mean_7'] = df[value_col].rolling(window=7).mean()
        df['rolling_std_7'] = df[value_col].rolling(window=7).std()
        
        return df
    
    def _get_feature_columns(self) -> list:
        """Get list of feature column names."""
        features = ['dayofweek', 'dayofmonth', 'month', 'weekofyear', 'is_weekend']
        features += [f'lag_{lag}' for lag in range(1, self.n_lags + 1)]
        features += ['rolling_mean_7', 'rolling_std_7']
        return features
    
    def fit(self, data: pd.DataFrame, date_col: str, value_col: str) -> None:
        """Fit XGBoost model to the data."""
        from xgboost import XGBRegressor
        
        is_valid, msg = self.validate_data(data, 60)
        if not is_valid:
            raise ValueError(msg)
        
        self.training_data = data.copy()
        self.date_col = date_col
        self.value_col = value_col
        self.last_date = data[date_col].max()
        
        # Create features
        df = self._create_features(data, date_col, value_col)
        
        # Remove rows with NaN (from lag features)
        df = df.dropna()
        
        # Store last values for prediction
        self.last_values = data[value_col].tail(max(self.n_lags, 7)).values.tolist()
        
        # Prepare training data
        feature_cols = self._get_feature_columns()
        X = df[feature_cols]
        y = df[value_col]
        
        # Train XGBoost
        self.xgb_model = XGBRegressor(
            n_estimators=self.n_estimators,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        self.xgb_model.fit(X, y)
        self.is_fitted = True
    
    def predict(self, periods: int) -> pd.DataFrame:
        """Generate forecasts using XGBoost."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction.")
        
        forecasts = []
        current_values = self.last_values.copy()
        
        future_dates = pd.date_range(
            start=self.last_date + pd.Timedelta(days=1),
            periods=periods,
            freq='D'
        )
        
        for date in future_dates:
            # Create feature row
            features = {
                'dayofweek': date.dayofweek,
                'dayofmonth': date.day,
                'month': date.month,
                'weekofyear': date.isocalendar()[1],
                'is_weekend': 1 if date.dayofweek >= 5 else 0
            }
            
            # Add lag features
            for lag in range(1, self.n_lags + 1):
                if lag <= len(current_values):
                    features[f'lag_{lag}'] = current_values[-lag]
                else:
                    features[f'lag_{lag}'] = current_values[0]
            
            # Add rolling features
            recent_7 = current_values[-7:] if len(current_values) >= 7 else current_values
            features['rolling_mean_7'] = np.mean(recent_7)
            features['rolling_std_7'] = np.std(recent_7) if len(recent_7) > 1 else 0
            
            # Make prediction
            X_pred = pd.DataFrame([features])
            forecast = self.xgb_model.predict(X_pred)[0]
            forecast = max(0, forecast)  # Ensure non-negative
            
            forecasts.append({
                'Date': date,
                'Forecast': forecast,
                'Model': self.name
            })
            
            # Update values for next prediction
            current_values.append(forecast)
        
        return pd.DataFrame(forecasts)
    
    def get_fitted_values(self) -> Optional[np.ndarray]:
        """Get in-sample fitted values."""
        if self.xgb_model is None:
            return None
        
        df = self._create_features(self.training_data, self.date_col, self.value_col)
        df = df.dropna()
        
        feature_cols = self._get_feature_columns()
        X = df[feature_cols]
        
        fitted = np.full(len(self.training_data), np.nan)
        start_idx = len(self.training_data) - len(df)
        fitted[start_idx:] = self.xgb_model.predict(X)
        
        return fitted
    
    def get_description(self) -> Dict[str, str]:
        """Get model description."""
        return {
            "brief": "Machine learning model using gradient boosted decision trees.",
            "how_it_works": "Converts time series into supervised learning:\n"
                          f"• Creates {self.n_lags} lag features (past values)\n"
                          "• Adds time features (day of week, month, etc.)\n"
                          "• Trains gradient boosted trees to predict next value",
            "when_to_use": "When data has complex non-linear patterns. "
                          "Good for data with multiple influencing factors.",
            "strengths": "• Captures complex patterns\n"
                        "• Handles non-linear relationships\n"
                        "• Robust to outliers\n"
                        "• Feature importance available\n"
                        "• High accuracy potential",
            "limitations": "• Requires feature engineering\n"
                          "• Less interpretable than statistical models\n"
                          "• No built-in confidence intervals\n"
                          "• May overfit on small datasets"
        }
