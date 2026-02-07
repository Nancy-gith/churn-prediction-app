"""
Configuration settings for Sales Forecasting Application
"""

# Application Settings
APP_TITLE = "📊 Sales Forecasting Dashboard"
APP_ICON = "📈"
PAGE_LAYOUT = "wide"

# Data Settings
DATE_COLUMN = "Date"
PRODUCT_COLUMN = "Product"
QUANTITY_COLUMN = "Quantity"
REQUIRED_COLUMNS = [DATE_COLUMN, PRODUCT_COLUMN, QUANTITY_COLUMN]

# Model Settings
MIN_DATA_POINTS_BASIC = 30
MIN_DATA_POINTS_ADVANCED = 60
DEFAULT_FORECAST_DAYS = 30
MAX_FORECAST_DAYS = 365

# Moving Average Settings
DEFAULT_SMA_WINDOW = 7
DEFAULT_WMA_WINDOW = 7

# ARIMA Settings
ARIMA_MAX_P = 5
ARIMA_MAX_D = 2
ARIMA_MAX_Q = 5

# Model Colors for Visualization
MODEL_COLORS = {
    "Historical": "#424242",
    "Simple Moving Average": "#2196F3",
    "Weighted Moving Average": "#4CAF50",
    "ARIMA": "#FF9800",
    "Prophet": "#9C27B0",
    "XGBoost": "#F44336"
}

# UI Theme Colors
THEME = {
    "primary": "#1E88E5",
    "secondary": "#43A047",
    "accent": "#FB8C00",
    "background": "#FAFAFA",
    "text": "#212121",
    "success": "#4CAF50",
    "warning": "#FF9800",
    "error": "#F44336"
}

# Sample Products for Demo Data
SAMPLE_PRODUCTS = [
    "Laptop Pro X1",
    "Wireless Mouse",
    "USB-C Hub",
    "Mechanical Keyboard",
    "Monitor 27inch"
]
