"""
Data Handler Module
Handles data loading, validation, preprocessing, and sample data generation.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Tuple, List, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    DATE_COLUMN, PRODUCT_COLUMN, QUANTITY_COLUMN,
    REQUIRED_COLUMNS, SAMPLE_PRODUCTS
)


def generate_sample_data(
    start_date: str = "2025-01-01",
    periods: int = 365,
    products: List[str] = None
) -> pd.DataFrame:
    """
    Generate realistic sample sales data with trends and seasonality.
    
    Args:
        start_date: Start date for the data
        periods: Number of days of data to generate
        products: List of product names
    
    Returns:
        DataFrame with Date, Product, and Quantity columns
    """
    if products is None:
        products = SAMPLE_PRODUCTS
    
    dates = pd.date_range(start=start_date, periods=periods, freq='D')
    data = []
    
    for product in products:
        # Base sales level (different for each product)
        np.random.seed(hash(product) % 2**32)
        base_sales = np.random.randint(50, 200)
        
        for i, date in enumerate(dates):
            # Trend component (slight upward trend)
            trend = i * 0.05
            
            # Weekly seasonality (higher on weekends)
            day_of_week = date.dayofweek
            weekly_effect = 20 if day_of_week >= 5 else 0
            
            # Monthly seasonality (higher at month end)
            day_of_month = date.day
            monthly_effect = 15 if day_of_month > 25 else 0
            
            # Random noise
            noise = np.random.normal(0, 10)
            
            # Calculate quantity
            quantity = max(0, int(base_sales + trend + weekly_effect + monthly_effect + noise))
            
            data.append({
                DATE_COLUMN: date,
                PRODUCT_COLUMN: product,
                QUANTITY_COLUMN: quantity
            })
    
    df = pd.DataFrame(data)
    return df.sort_values(DATE_COLUMN).reset_index(drop=True)


def load_data(file) -> Tuple[pd.DataFrame, List[str]]:
    """
    Load data from uploaded file (CSV or Excel).
    
    Args:
        file: Uploaded file object from Streamlit
    
    Returns:
        Tuple of (DataFrame, list of error messages)
    """
    errors = []
    df = None
    
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
        else:
            errors.append("Unsupported file format. Please upload CSV or Excel file.")
            return None, errors
    except Exception as e:
        errors.append(f"Error reading file: {str(e)}")
        return None, errors
    
    return df, errors


def validate_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validate that the DataFrame has required columns and proper data types.
    
    Args:
        df: Input DataFrame
    
    Returns:
        Tuple of (is_valid, list of error/warning messages)
    """
    messages = []
    is_valid = True
    
    # Check for required columns
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        messages.append(f"❌ Missing required columns: {', '.join(missing_cols)}")
        messages.append(f"   Expected columns: {', '.join(REQUIRED_COLUMNS)}")
        is_valid = False
        return is_valid, messages
    
    # Check date column
    try:
        df[DATE_COLUMN] = pd.to_datetime(df[DATE_COLUMN])
        messages.append(f"✅ Date column '{DATE_COLUMN}' is valid")
    except Exception:
        messages.append(f"❌ Could not parse '{DATE_COLUMN}' as dates")
        is_valid = False
    
    # Check quantity column
    if not pd.api.types.is_numeric_dtype(df[QUANTITY_COLUMN]):
        messages.append(f"❌ '{QUANTITY_COLUMN}' must be numeric")
        is_valid = False
    else:
        messages.append(f"✅ Quantity column '{QUANTITY_COLUMN}' is valid")
    
    # Check for missing values
    missing_count = df[REQUIRED_COLUMNS].isnull().sum().sum()
    if missing_count > 0:
        messages.append(f"⚠️ Found {missing_count} missing values")
    else:
        messages.append("✅ No missing values found")
    
    # Check data range
    if is_valid:
        date_range = (df[DATE_COLUMN].max() - df[DATE_COLUMN].min()).days
        messages.append(f"📅 Data spans {date_range} days")
        
        unique_products = df[PRODUCT_COLUMN].nunique()
        messages.append(f"📦 Found {unique_products} unique products")
    
    return is_valid, messages


def preprocess_data(
    df: pd.DataFrame,
    product: Optional[str] = None
) -> pd.DataFrame:
    """
    Preprocess data for forecasting.
    
    Args:
        df: Input DataFrame
        product: Optional product to filter by
    
    Returns:
        Preprocessed DataFrame
    """
    df = df.copy()
    
    # Ensure date column is datetime
    df[DATE_COLUMN] = pd.to_datetime(df[DATE_COLUMN])
    
    # Filter by product if specified
    if product and product != "All Products":
        df = df[df[PRODUCT_COLUMN] == product]
    
    # Aggregate by date (in case of multiple entries per date)
    df = df.groupby(DATE_COLUMN)[QUANTITY_COLUMN].sum().reset_index()
    
    # Sort by date
    df = df.sort_values(DATE_COLUMN).reset_index(drop=True)
    
    # Handle missing dates (fill with forward fill then backward fill)
    date_range = pd.date_range(start=df[DATE_COLUMN].min(), end=df[DATE_COLUMN].max(), freq='D')
    df = df.set_index(DATE_COLUMN).reindex(date_range).reset_index()
    df.columns = [DATE_COLUMN, QUANTITY_COLUMN]
    
    # Fill missing values
    df[QUANTITY_COLUMN] = df[QUANTITY_COLUMN].fillna(method='ffill').fillna(method='bfill')
    
    return df


def get_products(df: pd.DataFrame) -> List[str]:
    """
    Get list of unique products from DataFrame.
    
    Args:
        df: Input DataFrame
    
    Returns:
        List of product names
    """
    return sorted(df[PRODUCT_COLUMN].unique().tolist())


def get_data_summary(df: pd.DataFrame) -> dict:
    """
    Get summary statistics for the data.
    
    Args:
        df: Input DataFrame
    
    Returns:
        Dictionary with summary statistics
    """
    return {
        "total_rows": len(df),
        "date_range": f"{df[DATE_COLUMN].min().strftime('%Y-%m-%d')} to {df[DATE_COLUMN].max().strftime('%Y-%m-%d')}",
        "unique_products": df[PRODUCT_COLUMN].nunique(),
        "total_quantity": df[QUANTITY_COLUMN].sum(),
        "avg_daily_quantity": df.groupby(DATE_COLUMN)[QUANTITY_COLUMN].sum().mean()
    }


if __name__ == "__main__":
    # Generate and save sample data
    sample_df = generate_sample_data()
    sample_df.to_csv("sample_data/sample_sales_data.csv", index=False)
    print(f"Generated sample data with {len(sample_df)} rows")
    print(sample_df.head(10))
