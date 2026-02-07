# 📊 Sales Forecasting Web Application
## Complete Technical Documentation

**Created:** February 4, 2026  
**Author:** AI-Assisted Development  
**Version:** 1.0.0

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Installation & Setup](#2-installation--setup)
3. [Project Architecture](#3-project-architecture)
4. [Data Requirements](#4-data-requirements)
5. [Forecasting Models Explained](#5-forecasting-models-explained)
6. [Code Structure & Modules](#6-code-structure--modules)
7. [User Interface Guide](#7-user-interface-guide)
8. [Performance Metrics](#8-performance-metrics)
9. [Best Practices & Tips](#9-best-practices--tips)
10. [Troubleshooting](#10-troubleshooting)
11. [Future Enhancements](#11-future-enhancements)

---

## 1. Project Overview

### 1.1 What is This Application?

This is a **web-based sales forecasting dashboard** built with Streamlit that enables business analysts to:
- Upload historical sales data (CSV or Excel)
- Generate forecasts using 5 different time series models
- Compare model performance visually
- Understand which model works best for their data
- Learn about forecasting concepts through educational content

### 1.2 Target Users

- **Business Analysts** who need to predict future sales
- **Inventory Managers** planning stock levels
- **Marketing Teams** forecasting campaign impacts
- **Students** learning time series forecasting

### 1.3 Key Features

| Feature | Description |
|---------|-------------|
| Multi-Model Forecasting | 5 different models from basic to advanced |
| Interactive Visualizations | Plotly-powered charts with zoom, hover, export |
| Model Comparison | Side-by-side performance metrics |
| Educational Content | Learn about each model's strengths |
| Flexible Input | Support for CSV and Excel files |
| Sample Data | Built-in realistic sample data for testing |

---

## 2. Installation & Setup

### 2.1 Prerequisites

- **Python 3.8 or higher** (Python 3.10+ recommended)
- **pip** (Python package manager)
- **Virtual environment** (recommended)

### 2.2 Step-by-Step Installation

#### Step 1: Navigate to Project Directory
```cmd
cd "C:\Users\NANCY\OneDrive\Desktop\My Projects\SALES_FORECASTING"
```

#### Step 2: Activate Virtual Environment
```cmd
REM Using the Master_env created in parent folder
"..\Master_env\Scripts\activate.bat"
```
You should see `(Master_env)` appear in your command prompt.

#### Step 3: Install Dependencies
```cmd
pip install -r requirements.txt
```

This installs:
| Package | Version | Purpose |
|---------|---------|---------|
| streamlit | ≥1.28.0 | Web application framework |
| pandas | ≥2.0.0 | Data manipulation |
| numpy | ≥1.24.0 | Numerical computations |
| plotly | ≥5.18.0 | Interactive charts |
| statsmodels | ≥0.14.0 | ARIMA model |
| prophet | ≥1.1.4 | Facebook's forecasting tool |
| xgboost | ≥2.0.0 | Gradient boosting model |
| scikit-learn | ≥1.3.0 | Metrics & ML utilities |
| openpyxl | ≥3.1.0 | Excel file support |

#### Step 4: Run the Application
```cmd
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

### 2.3 Troubleshooting Installation

**Issue: Prophet installation fails**
```cmd
pip install pystan==2.19.1.1
pip install prophet
```

**Issue: XGBoost installation fails on Windows**
```cmd
pip install xgboost --no-cache-dir
```

---

## 3. Project Architecture

### 3.1 Folder Structure

```
SALES_FORECASTING/
│
├── app.py                      # Main Streamlit application entry point
├── config.py                   # Centralized configuration settings
├── requirements.txt            # Python package dependencies
├── README.md                   # Quick start guide
├── PROJECT_PLAN.md            # Development planning document
├── DOCUMENTATION.md           # This file - complete documentation
│
├── sample_data/
│   └── sample_sales_data.csv  # 1,825 rows of realistic sample data
│
├── src/                        # Source code modules
│   ├── __init__.py            # Package initializer
│   ├── data_handler.py        # Data loading, validation, preprocessing
│   ├── metrics.py             # Accuracy metric calculations
│   ├── visualization.py       # Plotly chart generation
│   │
│   └── models/                # Forecasting model implementations
│       ├── __init__.py        # Model exports
│       ├── base_model.py      # Abstract base class
│       ├── moving_average.py  # SMA & WMA implementations
│       ├── arima_model.py     # ARIMA implementation
│       ├── prophet_model.py   # Prophet implementation
│       └── xgboost_model.py   # XGBoost implementation
│
├── components/                 # UI component modules (extensible)
│   └── __init__.py
│
└── assets/
    └── style.css              # Custom CSS styling
```

### 3.2 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE (app.py)                      │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DATA LOADING (data_handler.py)                    │
│  • Load CSV/Excel files                                              │
│  • Validate column structure                                         │
│  • Generate sample data                                              │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  DATA PREPROCESSING (data_handler.py)                │
│  • Filter by product                                                 │
│  • Aggregate daily sales                                             │
│  • Handle missing values                                             │
│  • Sort by date                                                      │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    MODEL TRAINING (src/models/)                      │
│  ┌───────┐ ┌───────┐ ┌───────┐ ┌─────────┐ ┌─────────┐              │
│  │  SMA  │ │  WMA  │ │ ARIMA │ │ Prophet │ │ XGBoost │              │
│  └───────┘ └───────┘ └───────┘ └─────────┘ └─────────┘              │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   FORECAST GENERATION (src/models/)                  │
│  • Generate predictions for N future days                            │
│  • Calculate confidence intervals (where available)                  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
              ┌─────────────────────┴─────────────────────┐
              ▼                                           ▼
┌──────────────────────────┐              ┌──────────────────────────┐
│ METRICS (metrics.py)     │              │ VISUALIZATION            │
│ • Calculate MAE          │              │ (visualization.py)       │
│ • Calculate RMSE         │              │ • Historical charts      │
│ • Calculate MAPE         │              │ • Forecast comparison    │
│ • Compare models         │              │ • Metrics bar charts     │
└──────────────────────────┘              └──────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      USER INTERFACE DISPLAY                          │
│  • Interactive Plotly charts                                         │
│  • Performance metrics table                                         │
│  • Model explanations                                                │
│  • Export capabilities                                               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 4. Data Requirements

### 4.1 Required Columns

Your input data **must** have these three columns:

| Column Name | Data Type | Description | Example |
|-------------|-----------|-------------|---------|
| `Date` | datetime | Date of the sales record | 2025-01-15 |
| `Product` | string | Name or ID of the product | "Laptop Pro X1" |
| `Quantity` | integer | Number of units sold | 150 |

### 4.2 Example Data Format

```csv
Date,Product,Quantity
2025-01-01,Laptop Pro X1,145
2025-01-01,Wireless Mouse,89
2025-01-01,USB-C Hub,67
2025-01-02,Laptop Pro X1,152
2025-01-02,Wireless Mouse,95
...
```

### 4.3 Data Quality Guidelines

| Aspect | Requirement | Recommendation |
|--------|-------------|----------------|
| **Minimum Records** | 30 data points per product | 90+ for better accuracy |
| **Date Frequency** | Daily data preferred | Weekly/Monthly also works |
| **Missing Values** | Allowed but limited | Fill gaps before upload |
| **Negative Values** | Not allowed | Use 0 for no sales |

### 4.4 Sample Data Included

The project includes a pre-generated sample dataset with:
- **1,825 rows** of data
- **5 products**: Laptop Pro X1, Wireless Mouse, USB-C Hub, Mechanical Keyboard, Monitor 27inch
- **365 days** of historical data (full year)
- **Realistic patterns**: Trends, weekly seasonality, monthly effects

---

## 5. Forecasting Models Explained

### 5.1 Simple Moving Average (SMA)

**Category:** Basic Statistical Method

**How It Works:**
```
Forecast = (Sum of last N values) / N
```

For example, with a 7-day window:
```
Day 8 Forecast = (Day1 + Day2 + Day3 + Day4 + Day5 + Day6 + Day7) / 7
```

**When to Use:**
- ✅ Stable data without strong trends
- ✅ As a baseline for comparison
- ✅ When simplicity is valued

**Pros & Cons:**
| Pros | Cons |
|------|------|
| Very simple to understand | Lags behind trends |
| Fast computation | Equal weight to all periods |
| No hyperparameters | Cannot capture seasonality |

**Configuration in App:** Window size = 7 days (configurable in config.py)

---

### 5.2 Weighted Moving Average (WMA)

**Category:** Basic Statistical Method

**How It Works:**
```
Forecast = Σ(weight_i × value_i) / Σ(weight_i)
```

With linear weights, most recent data gets highest weight:
```
Weights for 7-day: [1, 2, 3, 4, 5, 6, 7]
Normalized: [0.036, 0.071, 0.107, 0.143, 0.179, 0.214, 0.250]
```

**When to Use:**
- ✅ Recent data is more relevant than older data
- ✅ Gradual trend changes expected
- ✅ Need slightly more responsiveness than SMA

**Pros & Cons:**
| Pros | Cons |
|------|------|
| More responsive to changes | Still lags sharp changes |
| Simple to understand | Weight selection arbitrary |
| Better than SMA for trends | No confidence intervals |

---

### 5.3 ARIMA (AutoRegressive Integrated Moving Average)

**Category:** Statistical Time Series Model

**How It Works:**

ARIMA(p, d, q) has three components:
- **AR(p)** - AutoRegressive: Uses past values to predict future
- **I(d)** - Integrated: Differencing to make data stationary  
- **MA(q)** - Moving Average: Uses past forecast errors

```
y_t = c + φ₁y_{t-1} + ... + φₚy_{t-p} + θ₁ε_{t-1} + ... + θ_qε_{t-q} + ε_t
```

**Auto-Parameter Selection:**
The app automatically finds the best (p, d, q) by testing combinations and selecting the one with lowest AIC (Akaike Information Criterion).

**When to Use:**
- ✅ Data has trends
- ✅ Need confidence intervals
- ✅ Want statistical foundations

**Pros & Cons:**
| Pros | Cons |
|------|------|
| Handles trends well | Assumes linear relationships |
| Provides confidence intervals | Needs stationary data |
| Well-established theory | Complex parameter tuning |

---

### 5.4 Prophet (Facebook Prophet)

**Category:** Advanced Decomposition Model

**How It Works:**

Prophet decomposes time series into components:
```
y(t) = g(t) + s(t) + h(t) + ε_t

Where:
g(t) = Trend (growth over time)
s(t) = Seasonality (weekly, yearly patterns)
h(t) = Holiday effects (optional)
ε_t  = Error term
```

**Automatic Features:**
- Detects yearly seasonality
- Detects weekly seasonality  
- Handles missing data automatically
- Robust to outliers

**When to Use:**
- ✅ Business data with multiple seasonalities
- ✅ Data has yearly and weekly patterns
- ✅ Need robust handling of missing data
- ✅ Want interpretable components

**Pros & Cons:**
| Pros | Cons |
|------|------|
| Automatic seasonality detection | Can overfit short series |
| Handles missing data | Slower than simple methods |
| Very interpretable | Requires more data (60+ points) |
| Uncertainty intervals included | May miss sudden changes |

---

### 5.5 XGBoost (Extreme Gradient Boosting)

**Category:** Machine Learning Model

**How It Works:**

Converts time series to supervised learning by creating features:

**Features Created:**
```python
# Time-based features
- dayofweek    (0-6)
- dayofmonth   (1-31)
- month        (1-12)
- weekofyear   (1-52)
- is_weekend   (0 or 1)

# Lag features
- lag_1 through lag_7 (past 7 values)

# Rolling statistics
- rolling_mean_7  (7-day average)
- rolling_std_7   (7-day std deviation)
```

Then trains gradient boosted decision trees to predict the next value.

**When to Use:**
- ✅ Complex non-linear patterns
- ✅ Multiple influencing factors
- ✅ Large datasets (more data = better)

**Pros & Cons:**
| Pros | Cons |
|------|------|
| Captures complex patterns | Requires feature engineering |
| High accuracy potential | Less interpretable |
| Robust to outliers | May overfit small datasets |
| Handles non-linear relationships | No built-in confidence intervals |

---

### 5.6 Model Comparison Summary

| Model | Complexity | Speed | Accuracy Potential | Best Data Size |
|-------|------------|-------|-------------------|----------------|
| SMA | ⭐ | ⚡⚡⚡ | ⭐⭐ | Any |
| WMA | ⭐ | ⚡⚡⚡ | ⭐⭐ | Any |
| ARIMA | ⭐⭐⭐ | ⚡⚡ | ⭐⭐⭐ | 30+ points |
| Prophet | ⭐⭐⭐⭐ | ⚡ | ⭐⭐⭐⭐ | 60+ points |
| XGBoost | ⭐⭐⭐⭐⭐ | ⚡⚡ | ⭐⭐⭐⭐⭐ | 100+ points |

---

## 6. Code Structure & Modules

### 6.1 config.py - Configuration Settings

Central location for all configurable parameters:

```python
# Column names (must match your data)
DATE_COLUMN = "Date"
PRODUCT_COLUMN = "Product"
QUANTITY_COLUMN = "Quantity"

# Minimum data requirements
MIN_DATA_POINTS_BASIC = 30      # For SMA, WMA, ARIMA
MIN_DATA_POINTS_ADVANCED = 60   # For Prophet, XGBoost

# Forecast settings
DEFAULT_FORECAST_DAYS = 30
MAX_FORECAST_DAYS = 365

# Model colors for visualization
MODEL_COLORS = {
    "Historical": "#424242",
    "Simple Moving Average": "#2196F3",
    "Weighted Moving Average": "#4CAF50",
    "ARIMA": "#FF9800",
    "Prophet": "#9C27B0",
    "XGBoost": "#F44336"
}
```

### 6.2 src/data_handler.py - Data Operations

**Key Functions:**

| Function | Purpose |
|----------|---------|
| `generate_sample_data()` | Creates realistic sample sales data |
| `load_data(file)` | Loads CSV or Excel files |
| `validate_data(df)` | Checks required columns and data types |
| `preprocess_data(df, product)` | Filters, aggregates, handles missing values |
| `get_products(df)` | Returns list of unique products |
| `get_data_summary(df)` | Returns statistics about the data |

### 6.3 src/metrics.py - Performance Metrics

**Metrics Calculated:**

```python
def calculate_mae(actual, predicted):
    """Mean Absolute Error - average error magnitude"""
    return mean(|actual - predicted|)

def calculate_rmse(actual, predicted):
    """Root Mean Square Error - penalizes large errors"""
    return sqrt(mean((actual - predicted)²))

def calculate_mape(actual, predicted):
    """Mean Absolute Percentage Error - percentage error"""
    return mean(|actual - predicted| / actual) × 100
```

### 6.4 src/models/base_model.py - Abstract Base Class

All models inherit from this class and must implement:

```python
class BaseForecaster(ABC):
    @abstractmethod
    def fit(self, data, date_col, value_col):
        """Train the model on historical data"""
        pass
    
    @abstractmethod
    def predict(self, periods):
        """Generate forecasts for N periods"""
        pass
    
    @abstractmethod
    def get_description(self):
        """Return educational content about the model"""
        pass
```

### 6.5 src/visualization.py - Chart Generation

**Available Charts:**

| Function | Chart Type |
|----------|------------|
| `plot_historical_data()` | Line chart of historical sales |
| `plot_forecast_comparison()` | Multi-model forecast overlay |
| `plot_single_forecast()` | Single model with confidence intervals |
| `plot_metrics_comparison()` | Bar chart comparing MAE, RMSE, MAPE |

---

## 7. User Interface Guide

### 7.1 Application Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│                      📊 Sales Forecasting Dashboard                  │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │  Welcome banner with gradient background                        ││
│  └─────────────────────────────────────────────────────────────────┘│
├─────────────────┬───────────────────────────────────────────────────┤
│    SIDEBAR      │                   MAIN CONTENT                    │
│                 │                                                   │
│ ⚙️ Configuration│   📋 Data Overview                               │
│                 │   ┌─────┬─────┬─────┬─────┐                      │
│ 📁 Data Source  │   │Total│Prods│Range│ Avg │  <- Metric cards    │
│ ○ Upload File   │   └─────┴─────┴─────┴─────┘                      │
│ ● Use Sample    │                                                   │
│                 │   📈 Historical Data Chart                       │
│ 📦 Product      │   [Interactive Plotly line chart]                │
│ [Dropdown ▼]    │                                                   │
│                 │   📊 Forecast Results                             │
│ 🔮 Forecast     │   ┌──────┬──────┬──────┬──────┐                  │
│ Days: [==30==]  │   │Compar│Indiv │Metric│Guide │ <- Tabs          │
│                 │   └──────┴──────┴──────┴──────┘                  │
│ 🤖 Models       │   [Tab content area]                             │
│ ☑ SMA           │                                                   │
│ ☑ WMA           │                                                   │
│ ☑ ARIMA         │                                                   │
│ ☑ Prophet       │                                                   │
│ ☑ XGBoost       │                                                   │
│                 │                                                   │
│ [🚀 Generate]   │                                                   │
└─────────────────┴───────────────────────────────────────────────────┘
```

### 7.2 Step-by-Step Usage

**Step 1: Load Data**
- Choose "Upload File" and select your CSV/Excel, OR
- Choose "Use Sample Data" and click "Generate Sample Data"

**Step 2: Select Product**
- Use dropdown to select a specific product
- Or keep "All Products" for aggregate analysis

**Step 3: Configure Forecast**
- Adjust the slider for forecast horizon (7-365 days)
- Default is 30 days

**Step 4: Select Models**
- Check/uncheck models to include in comparison
- All 5 selected by default

**Step 5: Generate Forecasts**
- Click "🚀 Generate Forecasts" button
- Wait for processing (progress bar shown)

**Step 6: Analyze Results**
- **Comparison View**: All models overlaid on one chart
- **Individual Models**: Detailed view with confidence intervals
- **Model Metrics**: MAE, RMSE, MAPE comparison
- **Model Guide**: Educational content about each model

---

## 8. Performance Metrics

### 8.1 Understanding the Metrics

#### MAE (Mean Absolute Error)
```
MAE = (1/n) × Σ|actual - predicted|
```
- **Interpretation**: Average error in the same units as your data
- **Example**: MAE of 15 means predictions are off by 15 units on average
- **When to use**: When all errors are equally important

#### RMSE (Root Mean Square Error)
```
RMSE = √[(1/n) × Σ(actual - predicted)²]
```
- **Interpretation**: Standard deviation of prediction errors
- **Key feature**: Penalizes large errors more heavily
- **When to use**: When big errors are particularly bad

#### MAPE (Mean Absolute Percentage Error)
```
MAPE = (100/n) × Σ|(actual - predicted) / actual|
```
- **Interpretation**: Average percentage error
- **Example**: MAPE of 10% means predictions are 10% off on average
- **When to use**: Comparing across different scales

### 8.2 Which Metric to Use?

| Scenario | Recommended Metric |
|----------|-------------------|
| Same product, same scale | MAE or RMSE |
| Comparing different products | MAPE |
| Large errors are costly | RMSE |
| All errors equal impact | MAE |
| Business stakeholder communication | MAPE |

---

## 9. Best Practices & Tips

### 9.1 Data Preparation

✅ **Do:**
- Fill obvious gaps in dates before uploading
- Ensure consistent date formatting
- Remove or flag obvious outliers
- Use at least 3 months of data for Prophet/XGBoost

❌ **Don't:**
- Mix different products in the same row
- Use text in the Quantity column
- Leave large gaps (>7 days) unfilled

### 9.2 Model Selection

| Data Characteristic | Recommended Model |
|--------------------|-------------------|
| Very short history (<30 days) | SMA, WMA only |
| Clear upward/downward trend | ARIMA |
| Weekly patterns (weekday vs weekend) | Prophet |
| Complex, irregular patterns | XGBoost |
| Need for simplicity | SMA (baseline) |

### 9.3 Forecast Horizon Guidelines

| Horizon | Confidence Level |
|---------|-----------------|
| 7 days | High confidence |
| 14-30 days | Good confidence |
| 30-90 days | Moderate confidence |
| 90+ days | Use with caution |

---

## 10. Troubleshooting

### 10.1 Common Issues

**Issue: "Insufficient data" warning**
```
Solution: Ensure you have at least 30 data points for basic models,
60+ for Prophet and XGBoost.
```

**Issue: Prophet model fails**
```
Solution: Prophet requires complete, gap-free data. 
Fill missing dates before uploading.
```

**Issue: App is slow**
```
Solution: 
1. Reduce forecast horizon
2. Select fewer models
3. Filter to single product instead of "All Products"
```

**Issue: Import errors when running**
```
Solution: Ensure all packages are installed:
pip install -r requirements.txt --force-reinstall
```

### 10.2 Error Messages Explained

| Error | Meaning | Solution |
|-------|---------|----------|
| "Missing required columns" | Data doesn't have Date/Product/Quantity | Rename columns to match |
| "Could not parse dates" | Date format not recognized | Use YYYY-MM-DD format |
| "Model must be fitted" | Code issue | Restart the app |

---

## 11. Future Enhancements

### Planned Features

- [ ] **Export Forecasts**: Download predictions as CSV/Excel
- [ ] **Holiday Effects**: Add custom holiday calendars
- [ ] **Ensemble Models**: Combine multiple models
- [ ] **Real-time Updates**: Connect to live data sources
- [ ] **API Endpoint**: RESTful API for programmatic access
- [ ] **Scheduled Forecasting**: Automated daily/weekly forecasts
- [ ] **Email Alerts**: Notify when actuals deviate from forecast

### Adding New Models

To add a new forecasting model:

1. Create new file in `src/models/your_model.py`
2. Inherit from `BaseForecaster`
3. Implement `fit()`, `predict()`, `get_description()`
4. Add to `src/models/__init__.py`
5. Add to model selection in `app.py`

---

## Appendix A: Sample Code Snippets

### Loading Your Own Data Programmatically

```python
import pandas as pd
from src.data_handler import validate_data, preprocess_data
from src.models import ARIMAForecaster

# Load data
df = pd.read_csv("your_data.csv")

# Validate
is_valid, messages = validate_data(df)
print(messages)

# Preprocess for specific product
processed = preprocess_data(df, "YourProduct")

# Train and forecast
model = ARIMAForecaster(auto_select=True)
model.fit(processed, "Date", "Quantity")
forecast = model.predict(periods=30)
print(forecast)
```

### Customizing Visualization Colors

In `config.py`:
```python
MODEL_COLORS = {
    "Historical": "#000000",        # Black
    "Simple Moving Average": "#FF6B6B",  # Red
    "Weighted Moving Average": "#4ECDC4", # Teal
    # ... add more
}
```

---

## Appendix B: Glossary

| Term | Definition |
|------|------------|
| **Time Series** | Data points ordered by time |
| **Forecast Horizon** | How far into the future to predict |
| **Seasonality** | Repeating patterns (daily, weekly, yearly) |
| **Trend** | Long-term increase or decrease |
| **Stationarity** | Statistical properties that don't change over time |
| **Lag Features** | Past values used as predictors |
| **Confidence Interval** | Range where true value likely falls |
| **Overfitting** | Model too tailored to training data |

---

**Document Version:** 1.0.0  
**Last Updated:** February 4, 2026  
**Total Pages:** ~25 pages equivalent

---

*For questions or issues, please refer to the troubleshooting section or create a GitHub issue.*
