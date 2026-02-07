# 📊 Sales Forecasting Dashboard

A comprehensive Streamlit-based web application for sales forecasting using multiple time series models.

## 🚀 Features

- **Data Upload**: Support for CSV and Excel files
- **Sample Data**: Generate realistic sales data for testing
- **5 Forecasting Models**:
  - Simple Moving Average (SMA)
  - Weighted Moving Average (WMA)
  - ARIMA (AutoRegressive Integrated Moving Average)
  - Prophet (Facebook's forecasting tool)
  - XGBoost (Gradient Boosted Trees)
- **Interactive Visualizations**: Plotly-powered charts with confidence intervals
- **Model Comparison**: Side-by-side performance metrics
- **Educational Component**: Learn about each model's strengths and use cases

## 📋 Requirements

- Python 3.8+
- See `requirements.txt` for all dependencies

## 🛠️ Installation

1. **Create and activate virtual environment:**
   ```bash
   # Windows CMD
   python -m venv venv
   venv\Scripts\activate
   
   # Windows PowerShell
   python -m venv venv
   .\venv\Scripts\Activate
   
   # Linux/Mac
   python -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   streamlit run app.py
   ```

## 📁 Project Structure

```
SALES_FORECASTING/
├── app.py                    # Main Streamlit application
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── PROJECT_PLAN.md          # Detailed project documentation
├── sample_data/
│   └── sample_sales_data.csv # Sample dataset
├── src/
│   ├── data_handler.py       # Data loading and preprocessing
│   ├── metrics.py            # Accuracy metrics (MAE, RMSE, MAPE)
│   ├── visualization.py      # Plotly visualization functions
│   └── models/
│       ├── base_model.py     # Abstract base class
│       ├── moving_average.py # SMA & WMA models
│       ├── arima_model.py    # ARIMA model
│       ├── prophet_model.py  # Prophet model
│       └── xgboost_model.py  # XGBoost model
├── components/               # UI components (extensible)
└── assets/
    └── style.css             # Custom styling
```

## 📊 Data Format

Your input data should have these columns:
| Column | Type | Description |
|--------|------|-------------|
| Date | datetime | Date of sales |
| Product | string | Product name |
| Quantity | integer | Units sold |

## 🤖 Model Descriptions

### Simple Moving Average (SMA)
Best for: Stable data without strong trends

### Weighted Moving Average (WMA)
Best for: Data where recent observations are more important

### ARIMA
Best for: Time series with trends (non-seasonal)

### Prophet
Best for: Business data with multiple seasonalities

### XGBoost
Best for: Complex patterns with non-linear relationships

## 📈 Performance Metrics

- **MAE**: Mean Absolute Error (average error magnitude)
- **RMSE**: Root Mean Square Error (penalizes large errors)
- **MAPE**: Mean Absolute Percentage Error (percentage error)

## 🎨 Screenshots

The dashboard provides:
1. Data upload and validation
2. Historical data visualization
3. Multi-model forecast comparison
4. Performance metrics comparison
5. Interactive model explanations

## 📝 License

MIT License

## 🙋 Support

For questions or issues, please open a GitHub issue.
