# Quick Reference Guide

## 🚀 Getting Started

### First Time Setup (Already Done ✓)
```powershell
cd "c:\Users\NANCY\OneDrive\Desktop\My Projects\WEATHER_FORECASTING"
python -m venv env
.\env\Scripts\pip install -r requirements.txt
```

### Running the Application
```powershell
# Activate virtual environment
.\env\Scripts\activate

# Run Streamlit app
streamlit run app.py

# Open browser at: http://localhost:8501
```

### Stopping the Application
- Press `Ctrl+C` in the terminal
- Or close the terminal window

---

## 📁 Project Structure

```
WEATHER_FORECASTING/
├── app.py                    # Main landing page
├── requirements.txt          # Python dependencies
├── README.md                 # Project overview
├── PROJECT_PLAN.md          # Detailed planning document
├── IMPLEMENTATION_STATUS.md  # Current progress tracker
│
├── .streamlit/
│   └── config.toml          # App theme configuration
│
├── pages/
│   └── 1_Dashboard.py       # Data loading & visualization page
│
├── utils/
│   ├── __init__.py
│   ├── data_loader.py       # Meteostat API integration
│   └── preprocessing.py     # Feature engineering
│
├── models/
│   └── saved/               # Trained model storage (empty for now)
│
├── data/
│   ├── raw/                 # Downloaded CSV files (cached)
│   └── processed/           # Cleaned/engineered data
│
└── env/                     # Virtual environment (don't commit)
```

---

## 🎮 Using the Application

### Step 1: Launch
```powershell
streamlit run app.py
```

### Step 2: Navigate to Dashboard
- Click "📊 Dashboard" in the sidebar
- Or visit: http://localhost:8501/Dashboard

### Step 3: Load Data
1. Select a city from the dropdown (e.g., "London")
2. Choose years of historical data (1-10)
3. Click "🔄 Load Data"
4. Wait 5-10 seconds for data to download and cache

### Step 4: Explore
- **Temperature Trends**: Interactive time series chart
- **Precipitation**: Area chart showing rainfall patterns
- **Wind Speed**: Histogram distribution
- **Feature Engineering**: See 30+ engineered features

---

## 🔧 Common Tasks

### Add a New City
Edit `utils/data_loader.py`, line ~40:
```python
city_database = {
    'london': {'name': 'London', 'lat': 51.5074, 'lon': -0.1278, 'country': 'GB'},
    'your_city': {'name': 'Your City', 'lat': XX.XXXX, 'lon': YY.YYYY, 'country': 'CC'},
    # ... other cities
}
```

### Clear Cached Data
Delete files in `data/raw/` to force re-download from Meteostat

### Change Theme Colors
Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#FF4B4B"      # Change this
backgroundColor = "#0E1117"   # Or this
```

---

## 🐛 Troubleshooting

### "Module not found" error
**Solution**: Ensure virtual environment is activated
```powershell
.\env\Scripts\activate
pip list  # Should show all installed packages
```

### Port already in use
**Solution**: Streamlit uses port 8501 by default
```powershell
# Use a different port
streamlit run app.py --server.port 8502
```

### Data not loading
**Solution**: Check internet connection (Meteostat requires network access)

### Streamlit "Script changed" warning
**Solution**: That's normal! Streamlit auto-reloads when you edit files

---

## 📚 Key Libraries Documentation

- **Streamlit**: https://docs.streamlit.io/
- **Meteostat**: https://dev.meteostat.net/python/
- **Plotly**: https://plotly.com/python/
- **Prophet**: https://facebook.github.io/prophet/
- **XGBoost**: https://xgboost.readthedocs.io/
- **TensorFlow**: https://www.tensorflow.org/api_docs

---

## 🎯 Next Development Tasks

### To implement Prophet model:
1. Create `models/prophet_model.py`
2. Create `pages/2_Prophet_Forecasts.py`
3. Train on Dashboard-loaded data
4. Display 7-day forecast

### To implement XGBoost model:
1. Create `models/xgboost_model.py`
2. Create `pages/3_XGBoost_Forecasts.py`
3. Show feature importance

### To implement LSTM model:
1. Create `models/lstm_model.py`
2. Create `pages/4_LSTM_Forecasts.py`
3. Show training history

---

## 💡 Quick Tips

- **Data loads slowly first time**: It's downloading from Meteostat. Subsequent loads use cache.
- **Feature count**: We create 30+ features from just 6 raw columns!
- **Session state**: Data persists across pages (stored in `st.session_state`)
- **Dark theme**: Configured in `.streamlit/config.toml`
- **Auto-reload**: Streamlit watches for file changes and reloads automatically

---

## 🎓 For Learning

### Understanding the Data Pipeline:
1. Read `utils/data_loader.py` - See how we fetch and cache data
2. Read `utils/preprocessing.py` - See how we engineer features
3. Try modifying lag windows or rolling window sizes

### Understanding Streamlit:
1. Check `app.py` - Simple welcome page
2. Check `pages/1_Dashboard.py` - Complex interactive page
3. Notice how `st.session_state` shares data between pages

### Understanding the Models (Coming Soon):
1. Prophet: Additive model with trend + seasonality
2. XGBoost: Gradient boosting on lag features
3. LSTM: Recurrent neural network for sequences

---

*Keep this file handy as your quick reference while developing!*
