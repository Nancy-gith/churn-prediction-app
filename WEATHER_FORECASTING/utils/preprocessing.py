"""
Data Preprocessing Module for Weather Forecasting

Handles data cleaning, feature engineering, and preparation for ML models.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import streamlit as st


class WeatherPreprocessor:
    """
    Preprocesses weather data for machine learning models.
    
    Handles missing values, feature engineering, and normalization.
    """
    
    def __init__(self):
        """Initialize the preprocessor with scalers."""
        self.scaler = MinMaxScaler()
        self.is_fitted = False
    
    @staticmethod
    def clean_data(df: pd.DataFrame, interpolate_method: str = 'linear') -> pd.DataFrame:
        """
        Clean the raw weather data by handling missing values.
        
        Parameters:
            df (pd.DataFrame): Raw weather data
            interpolate_method (str): Method for interpolation ('linear', 'time', 'polynomial')
        
        Returns:
            pd.DataFrame: Cleaned data
        """
        df_clean = df.copy()
        
        # Interpolate missing values for numeric columns
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        df_clean[numeric_cols] = df_clean[numeric_cols].interpolate(method=interpolate_method)
        
        # Forward fill any remaining NaN values at the edges
        df_clean = df_clean.fillna(method='ffill').fillna(method='bfill')
        
        return df_clean
    
    @staticmethod
    def create_lag_features(df: pd.DataFrame, target_col: str = 'tavg', 
                           lags: list = [1, 7, 14, 30]) -> pd.DataFrame:
        """
        Create lagged features for time series prediction.
        
        Parameters:
            df (pd.DataFrame): Input data
            target_col (str): Column to create lags for
            lags (list): List of lag periods (e.g., [1, 7] for 1-day and 7-day lags)
        
        Returns:
            pd.DataFrame: Data with lag features added
        """
        df_with_lags = df.copy()
        
        for lag in lags:
            df_with_lags[f'{target_col}_lag_{lag}'] = df_with_lags[target_col].shift(lag)
        
        return df_with_lags
    
    @staticmethod
    def create_rolling_features(df: pd.DataFrame, target_col: str = 'tavg',
                               windows: list = [7, 14, 30]) -> pd.DataFrame:
        """
        Create rolling mean and std features.
        
        Parameters:
            df (pd.DataFrame): Input data
            target_col (str): Column to calculate rolling statistics for
            windows (list): List of window sizes
        
        Returns:
            pd.DataFrame: Data with rolling features added
        """
        df_with_rolling = df.copy()
        
        for window in windows:
            df_with_rolling[f'{target_col}_rolling_mean_{window}'] = \
                df_with_rolling[target_col].rolling(window=window).mean()
            df_with_rolling[f'{target_col}_rolling_std_{window}'] = \
                df_with_rolling[target_col].rolling(window=window).std()
        
        return df_with_rolling
    
    @staticmethod
    def create_cyclical_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Create cyclical features from date (sin/cos encodings).
        
        This helps models understand that December 31 and January 1 are close together.
        
        Parameters:
            df (pd.DataFrame): Input data with datetime index
        
        Returns:
            pd.DataFrame: Data with cyclical features added
        """
        df_with_cyclical = df.copy()
        
        # Extract date components
        df_with_cyclical['day_of_year'] = df_with_cyclical.index.dayofyear
        df_with_cyclical['month'] = df_with_cyclical.index.month
        df_with_cyclical['day_of_week'] = df_with_cyclical.index.dayofweek
        
        # Convert to cyclical features using sin/cos
        df_with_cyclical['day_of_year_sin'] = np.sin(2 * np.pi * df_with_cyclical['day_of_year'] / 365)
        df_with_cyclical['day_of_year_cos'] = np.cos(2 * np.pi * df_with_cyclical['day_of_year'] / 365)
        
        df_with_cyclical['month_sin'] = np.sin(2 * np.pi * df_with_cyclical['month'] / 12)
        df_with_cyclical['month_cos'] = np.cos(2 * np.pi * df_with_cyclical['month'] / 12)
        
        df_with_cyclical['day_of_week_sin'] = np.sin(2 * np.pi * df_with_cyclical['day_of_week'] / 7)
        df_with_cyclical['day_of_week_cos'] = np.cos(2 * np.pi * df_with_cyclical['day_of_week'] / 7)
        
        return df_with_cyclical
    
    @staticmethod
    def engineer_features(df: pd.DataFrame, target_col: str = 'tavg') -> pd.DataFrame:
        """
        Apply all feature engineering steps.
        
        Parameters:
            df (pd.DataFrame): Cleaned weather data
            target_col (str): Target column for prediction
        
        Returns:
            pd.DataFrame: Data with all engineered features
        """
        df_engineered = df.copy()
        
        # Create lag features
        df_engineered = WeatherPreprocessor.create_lag_features(df_engineered, target_col)
        
        # Create rolling features
        df_engineered = WeatherPreprocessor.create_rolling_features(df_engineered, target_col)
        
        # Create cyclical date features
        df_engineered = WeatherPreprocessor.create_cyclical_features(df_engineered)
        
        # Drop rows with NaN created by lag/rolling features
        df_engineered = df_engineered.dropna()
        
        return df_engineered
    
    def normalize_data(self, df: pd.DataFrame, columns: list = None) -> pd.DataFrame:
        """
        Normalize data to [0, 1] range using MinMaxScaler.
        
        Parameters:
            df (pd.DataFrame): Input data
            columns (list, optional): Columns to normalize. If None, normalize all numeric columns.
        
        Returns:
            pd.DataFrame: Normalized data
        """
        df_normalized = df.copy()
        
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not self.is_fitted:
            df_normalized[columns] = self.scaler.fit_transform(df[columns])
            self.is_fitted = True
        else:
            df_normalized[columns] = self.scaler.transform(df[columns])
        
        return df_normalized
    
    def inverse_transform(self, data: np.ndarray, column_name: str = None) -> np.ndarray:
        """
        Inverse transform normalized data back to original scale.
        
        Parameters:
            data (np.ndarray): Normalized data
            column_name (str, optional): Name of the column to inverse transform
        
        Returns:
            np.ndarray: Data in original scale
        """
        if not self.is_fitted:
            raise ValueError("Scaler has not been fitted yet. Call normalize_data first.")
        
        return self.scaler.inverse_transform(data)
    
    @staticmethod
    @st.cache_data
    def prepare_for_prophet(df: pd.DataFrame, target_col: str = 'tavg') -> pd.DataFrame:
        """
        Prepare data in Prophet's required format.
        
        Prophet expects columns named 'ds' (datestamp) and 'y' (value to predict).
        
        Parameters:
            df (pd.DataFrame): Input data with datetime index
            target_col (str): Target column to predict
        
        Returns:
            pd.DataFrame: Data formatted for Prophet (columns: ds, y)
        """
        prophet_df = pd.DataFrame({
            'ds': df.index,
            'y': df[target_col].values
        })
        return prophet_df
    
    @staticmethod
    @st.cache_data
    def prepare_for_xgboost(df: pd.DataFrame, target_col: str = 'tavg', 
                           test_size: float = 0.2) -> tuple:
        """
        Prepare data for XGBoost training.
        
        Parameters:
            df (pd.DataFrame): Feature-engineered data
            target_col (str): Target column
            test_size (float): Fraction of data to use for testing
        
        Returns:
            tuple: (X_train, X_test, y_train, y_test)
        """
        # Remove target from features
        feature_cols = [col for col in df.columns if col != target_col and 
                       not col.startswith('Unnamed')]
        
        # Ensure we only use numeric features
        feature_cols = [col for col in feature_cols if df[col].dtype in [np.float64, np.int64]]
        
        X = df[feature_cols]
        y = df[target_col]
        
        # Split into train and test
        split_index = int(len(df) * (1 - test_size))
        X_train, X_test = X[:split_index], X[split_index:]
        y_train, y_test = y[:split_index], y[split_index:]
        
        return X_train, X_test, y_train, y_test
    
    @staticmethod
    @st.cache_data
    def prepare_for_lstm(df: pd.DataFrame, target_col: str = 'tavg',
                        sequence_length: int = 30, test_size: float = 0.2) -> tuple:
        """
        Prepare 3D sequences for LSTM training.
        
        Parameters:
            df (pd.DataFrame): Normalized feature data
            target_col (str): Target column
            sequence_length (int): Number of time steps to look back
            test_size (float): Fraction of data for testing
        
        Returns:
            tuple: (X_train, X_test, y_train, y_test) where X is 3D (samples, timesteps, features)
        """
        # Select features (exclude target from features in this simple implementation)
        feature_cols = [target_col]  # For simplicity, just use the target itself for univariate LSTM
        
        data = df[feature_cols].values
        
        X, y = [], []
        for i in range(sequence_length, len(data)):
            X.append(data[i - sequence_length:i])
            y.append(data[i, 0])  # Predict the target column
        
        X, y = np.array(X), np.array(y)
        
        # Split into train and test
        split_index = int(len(X) * (1 - test_size))
        X_train, X_test = X[:split_index], X[split_index:]
        y_train, y_test = y[:split_index], y[split_index:]
        
        return X_train, X_test, y_train, y_test


# Example usage
if __name__ == "__main__":
    # Create sample data
    dates = pd.date_range(start='2020-01-01', end='2023-01-01', freq='D')
    sample_data = pd.DataFrame({
        'tavg': np.random.randn(len(dates)).cumsum() + 15,
        'tmin': np.random.randn(len(dates)).cumsum() + 10,
        'tmax': np.random.randn(len(dates)).cumsum() + 20,
    }, index=dates)
    
    # Test preprocessing
    preprocessor = WeatherPreprocessor()
    
    print("Original data shape:", sample_data.shape)
    
    # Clean and engineer features
    cleaned = preprocessor.clean_data(sample_data)
    engineered = preprocessor.engineer_features(cleaned)
    
    print("After feature engineering:", engineered.shape)
    print("\nNew features:")
    print(engineered.columns.tolist())
