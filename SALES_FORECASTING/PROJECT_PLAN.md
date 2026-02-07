# Sales Forecasting Web Application - Project Plan

## 📋 Project Overview
A Streamlit-based sales forecasting application that enables business analysts to upload sales data and generate forecasts using 5 different time series models.

---

## 🏗️ Architecture Plan

### Folder Structure
```
SALES_FORECASTING/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── config.py                 # Configuration settings
├── README.md                 # Project documentation
├── sample_data/
│   └── sample_sales_data.csv # Sample dataset for testing
├── src/
│   ├── __init__.py
│   ├── data_handler.py       # Data loading, validation, preprocessing
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base_model.py     # Abstract base class for models
│   │   ├── moving_average.py # SMA & WMA implementations
│   │   ├── arima_model.py    # ARIMA implementation
│   │   ├── prophet_model.py  # Prophet implementation
│   │   └── xgboost_model.py  # XGBoost implementation
│   ├── visualization.py      # Plotting functions
│   ├── metrics.py            # Performance metrics (MAE, RMSE, MAPE)
│   └── utils.py              # Utility functions
├── components/
│   ├── __init__.py
│   ├── sidebar.py            # Sidebar components
│   ├── upload_section.py     # File upload UI
│   ├── forecast_section.py   # Forecasting UI
│   └── results_section.py    # Results display UI
└── assets/
    └── style.css             # Custom CSS styling
```

### Data Flow Diagram
```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  CSV/Excel  │────▶│   Validate   │────▶│  Preprocess │
│   Upload    │     │    Data      │     │    Data     │
└─────────────┘     └──────────────┘     └─────────────┘
                                                │
                                                ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Visualize  │◀────│   Generate   │◀────│   Select    │
│   Results   │     │   Forecast   │     │   Models    │
└─────────────┘     └──────────────┘     └─────────────┘
```

---

## 📦 Technical Stack

| Library | Version | Purpose |
|---------|---------|---------|
| streamlit | >=1.28.0 | Web application framework |
| pandas | >=2.0.0 | Data manipulation |
| numpy | >=1.24.0 | Numerical computations |
| plotly | >=5.18.0 | Interactive visualizations |
| statsmodels | >=0.14.0 | ARIMA model |
| prophet | >=1.1.4 | Facebook Prophet model |
| xgboost | >=2.0.0 | XGBoost model |
| scikit-learn | >=1.3.0 | Metrics & preprocessing |
| openpyxl | >=3.1.0 | Excel file support |

---

## 🤖 Forecasting Models

### 1. Simple Moving Average (SMA)
- **How it works:** Averages last N observations
- **Best for:** Stable data without strong trends
- **Strengths:** Simple, interpretable, no training needed
- **Limitations:** Lags behind trends, equal weight to all periods

### 2. Weighted Moving Average (WMA)
- **How it works:** Recent observations get higher weights
- **Best for:** Data with gradual trends
- **Strengths:** More responsive to recent changes
- **Limitations:** Requires weight selection, still lags

### 3. ARIMA (AutoRegressive Integrated Moving Average)
- **How it works:** Combines autoregression, differencing, and moving average
- **Best for:** Non-seasonal time series with trends
- **Strengths:** Handles trends, well-established statistical foundation
- **Limitations:** Requires stationarity, parameter tuning (p,d,q)

### 4. Prophet (Recommended Advanced #1)
- **Why chosen:** Facebook's robust forecasting tool, handles seasonality automatically
- **Best for:** Business data with multiple seasonalities, holidays
- **Strengths:** Automatic seasonality detection, handles missing data, interpretable
- **Limitations:** Can overfit on short series, slower than simple methods

### 5. XGBoost (Recommended Advanced #2)
- **Why chosen:** Powerful ML model, captures complex patterns
- **Best for:** Data with complex non-linear relationships
- **Strengths:** High accuracy, handles many features, robust
- **Limitations:** Requires feature engineering, less interpretable

---

## 🎨 UI/UX Design

### Layout Structure
```
┌────────────────────────────────────────────────────────────┐
│                    📊 Sales Forecaster                      │
├──────────────┬─────────────────────────────────────────────┤
│   SIDEBAR    │              MAIN CONTENT                    │
│              │                                              │
│ ┌──────────┐ │  ┌─────────────────────────────────────────┐│
│ │ Upload   │ │  │         Data Preview Table              ││
│ │ Data     │ │  └─────────────────────────────────────────┘│
│ └──────────┘ │                                              │
│              │  ┌─────────────────────────────────────────┐│
│ ┌──────────┐ │  │      Historical Data Chart              ││
│ │ Select   │ │  └─────────────────────────────────────────┘│
│ │ Product  │ │                                              │
│ └──────────┘ │  ┌─────────────────────────────────────────┐│
│              │  │       Forecast Results                   ││
│ ┌──────────┐ │  │    (Multiple model overlay)             ││
│ │ Forecast │ │  └─────────────────────────────────────────┘│
│ │ Days     │ │                                              │
│ └──────────┘ │  ┌─────────────────────────────────────────┐│
│              │  │      Model Comparison Metrics            ││
│ ┌──────────┐ │  │   MAE | RMSE | MAPE for each model      ││
│ │ Select   │ │  └─────────────────────────────────────────┘│
│ │ Models   │ │                                              │
│ └──────────┘ │  ┌─────────────────────────────────────────┐│
│              │  │      Model Explanations                  ││
│ [Generate]   │  │   (Expandable sections)                 ││
└──────────────┴──┴─────────────────────────────────────────┘│
```

### Color Scheme
- **Primary:** #1E88E5 (Blue)
- **Secondary:** #43A047 (Green)
- **Accent:** #FB8C00 (Orange)
- **Background:** #FAFAFA
- **Model Colors:**
  - SMA: #2196F3
  - WMA: #4CAF50
  - ARIMA: #FF9800
  - Prophet: #9C27B0
  - XGBoost: #F44336

---

## 📊 Development Phases

### Phase 1: Foundation (Day 1-2)
- [x] Project structure setup
- [ ] Data handler module
- [ ] Sample data generation
- [ ] Basic Streamlit app skeleton

### Phase 2: Core Models (Day 3-4)
- [ ] SMA & WMA implementation
- [ ] ARIMA implementation
- [ ] Model base class

### Phase 3: Advanced Models (Day 5-6)
- [ ] Prophet implementation
- [ ] XGBoost implementation
- [ ] Metrics module

### Phase 4: Visualization (Day 7)
- [ ] Plotly charts
- [ ] Model comparison views
- [ ] Confidence intervals

### Phase 5: UI Polish (Day 8-9)
- [ ] Custom CSS styling
- [ ] Error handling
- [ ] Tooltips & help text

### Phase 6: Testing & Documentation (Day 10)
- [ ] Edge case testing
- [ ] Documentation
- [ ] Sample data validation

---

## ❓ Answers to Your Questions

### 1. Handling Products with Insufficient Data
- **Minimum requirement:** 30 data points for basic models, 60+ for Prophet/XGBoost
- **Strategy:** Show warning, disable advanced models, offer SMA/WMA only

### 2. Handling Missing Values
- **Approach:** Forward fill for small gaps (≤3 days), linear interpolation for larger gaps
- **Display:** Show data quality indicator to user

### 3. Product-Specific vs Aggregate Forecasts
- **Recommendation:** Product-specific by default (more actionable)
- **Option:** Add "All Products" aggregate option in UI

### 4. Seasonal vs Non-Seasonal Products
- **Detection:** Use seasonal decomposition test automatically
- **Handling:** Prophet handles automatically; for ARIMA, use seasonal ARIMA (SARIMA)

### 5. Validation Metrics to Display
- **MAE:** Easy to interpret (average error in units)
- **RMSE:** Penalizes large errors (good for outliers)
- **MAPE:** Percentage error (for business context)
- **Display:** Bar chart comparison + best model highlight

---

## 🚀 Next Steps
1. Create all source files
2. Generate sample data
3. Implement models one by one
4. Build UI components
5. Test and refine

