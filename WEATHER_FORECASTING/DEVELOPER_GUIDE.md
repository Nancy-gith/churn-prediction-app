# 👨‍💻 Developer Guide - Code Walkthrough

## Quick Navigation
1. [Project Setup](#project-setup)
2. [Code Structure](#code-structure)
3. [Key Modules Explained](#key-modules-explained)
4. [Adding New Features](#adding-new-features)
5. [Common Tasks](#common-tasks)
6. [Debugging Guide](#debugging-guide)

---

## Project Setup

### Prerequisites
```bash
# Python 3.8+
python --version

# Virtual environment (recommended)
python -m venv env
.\env\Scripts\activate  # Windows
source env/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Required Packages
```txt
streamlit>=2.0.0       # Web framework
pandas>=2.0.0          # Data manipulation
meteostat>=1.6.0       # Historical weather
requests>=2.28.0       # API calls
plotly>=5.0.0          # Interactive charts
python-dotenv>=1.0.0   # Environment variables
geopy>=2.4.0          # Geocoding (optional)
```

### Environment Setup
```bash
# 1. Create .env file
OPENWEATHERMAP_API_KEY=your_key_here

# 2. Run the app
streamlit run app.py

# 3. Open browser
# http://localhost:8501
```

---

## Code Structure

### Directory Tree
```
WEATHER_FORECASTING/
├── app.py                      # Main entry point (landing page)
├── pages/
│   └── 1_Dashboard.py         # Real-time weather dashboard
├── utils/
│   ├── data_loader.py         # Data fetching & caching
│   └── preprocessing.py       # Feature engineering
├── data/
│   └── raw/                   # Cached CSV files
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── .env                       # API keys (not in git)
├── .env.example               # Template for .env
├── requirements.txt           # Python dependencies
└── README.md                  # Project overview
```

### Execution Flow
```
1. User runs: streamlit run app.py
        ↓
2. Streamlit loads app.py (landing page)
        ↓
3. User navigates to Dashboard (pages/1_Dashboard.py)
        ↓
4. Dashboard imports:
   - utils/data_loader.py
   - utils/preprocessing.py
        ↓
5. User selects city
        ↓
6. Data loader:
   - Checks cache
   - Fetches from API/Meteostat
   - Saves to data/raw/
        ↓
7. Preprocessor:
   - Cleans data
   - Calculates features
        ↓
8. Dashboard displays:
   - Weather cards
   - Interactive charts
```

---

## Key Modules Explained

### 1. `app.py` - Landing Page

**Purpose**: Welcome page with navigation

**Key Code:**
```python
import streamlit as st

# Page configuration (must be first Streamlit command)
st.set_page_config(
    page_title="Weather Forecasting - India",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("🌤️ Weather Forecasting Web Application")
st.markdown("""
Welcome to your comprehensive weather dashboard...
""")

# Columns for features
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### 🌡️ Real-Time Weather")
with col2:
    st.markdown("### 📊 Historical Data")
with col3:
    st.markdown("### 🤖 ML Models")

# Sidebar navigation hint
with st.sidebar:
    st.markdown("## 📍 Navigation")
    st.info("Use the sidebar to navigate between pages")
```

**Important:**
- `st.set_page_config()` MUST be the first Streamlit command
- Multi-page apps auto-create navigation from `pages/` folder
- File naming: `1_PageName.py` - number controls order

---

### 2. `utils/data_loader.py` - Data Fetching

**Purpose**: Fetch real-time and historical weather data

#### **Class Structure**
```python
class WeatherDataLoader:
    # Class variable: city database
    INDIAN_CITIES = {
        'mumbai': {'name': 'Mumbai', 'lat': 19.076, 'lon': 72.8777, ...}
    }
    
    def __init__(self, data_dir="data/raw", cache_days=1):
        self.data_dir = data_dir
        self.cache_days = cache_days
        self.api_key = os.getenv('OPENWEATHERMAP_API_KEY', '')
        os.makedirs(data_dir, exist_ok=True)
    
    @staticmethod
    def get_city_list():
        """Return sorted list of city names"""
        
    @staticmethod
    def get_city_info(city_name: str) -> dict:
        """Get coordinates for a city"""
        
    @st.cache_data(ttl=1800)
    def get_realtime_weather(city_name: str) -> dict:
        """Fetch current weather (cached 30 min)"""
        
    @st.cache_data(ttl=86400)
    def fetch_historical_data(city_name: str, days=30) -> pd.DataFrame:
        """Fetch 30-day history (cached 24 hours)"""
```

#### **Key Method: `get_realtime_weather()`**
```python
@st.cache_data(ttl=1800)  # Cache for 30 minutes
def get_realtime_weather(_self, city_name: str) -> dict:
    """
    Fetch real-time weather from OpenWeatherMap.
    
    Args:
        city_name: Name of city (e.g., "Mumbai")
        
    Returns:
        dict with keys:
            - temperature (float): °C
            - feels_like (float): °C
            - humidity (int): %
            - pressure (int): hPa
            - wind_speed (float): km/h
            - description (str): "Clear Sky"
            - icon (str): "01d"
            - clouds (int): %
            - visibility (float): km
            - timestamp (datetime)
    """
    # 1. Check if API key exists
    if not _self.api_key or _self.api_key == 'your_api_key_here':
        return _self._get_mock_weather(city_name)
    
    try:
        # 2. Get city coordinates
        city_info = WeatherDataLoader.get_city_info(city_name)
        
        # 3. Build API request
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            'lat': city_info['lat'],
            'lon': city_info['lon'],
            'appid': _self.api_key,
            'units': 'metric'  # Celsius
        }
        
        # 4. Make HTTP request
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Raise exception for 4xx/5xx
        data = response.json()
        
        # 5. Parse and transform response
        return {
            'temperature': round(data['main']['temp'], 1),
            'feels_like': round(data['main']['feels_like'], 1),
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'wind_speed': round(data['wind']['speed'] * 3.6, 1),  # m/s → km/h
            'description': data['weather'][0]['description'].title(),
            'icon': data['weather'][0]['icon'],
            'icon_url': f"http://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png",
            'clouds': data['clouds']['all'],
            'visibility': data.get('visibility', 10000) / 1000,  # m → km
            'timestamp': datetime.fromtimestamp(data['dt'])
        }
        
    except Exception as e:
        # 6. Fallback to mock data on error
        st.warning(f"API error: {str(e)}. Using sample data.")
        return _self._get_mock_weather(city_name)
```

**Why `_self` instead of `self`?**
- Streamlit caching requires underscore prefix for ignored parameters
- `_self` is not included in cache key
- Only `city_name` determines cache uniqueness

#### **Key Method: `fetch_historical_data()`**
```python
@st.cache_data(ttl=86400)  # Cache for 24 hours
def fetch_historical_data(_self, city_name: str, days: int = 30) -> pd.DataFrame:
    """
    Fetch historical weather data from Meteostat.
    
    Returns DataFrame with columns:
        - date (index): datetime
        - tavg: Average temperature (°C)
        - tmin: Min temperature (°C)
        - tmax: Max temperature (°C)
        - prcp: Precipitation (mm)
        - wspd: Wind speed (km/h)
        - pres: Pressure (hPa)
    """
    # 1. Check file cache first
    cache_file = os.path.join(
        _self.data_dir, 
        f"{city_name.lower().replace(' ', '_')}_30days.csv"
    )
    
    if os.path.exists(cache_file):
        # Check if cache is fresh (< 24 hours old)
        file_age = datetime.now() - datetime.fromtimestamp(
            os.path.getmtime(cache_file)
        )
        if file_age.days < _self.cache_days:
            # Load from cache
            df = pd.read_csv(cache_file, parse_dates=['date'])
            df.set_index('date', inplace=True)
            return df
    
    # 2. Fetch fresh data from Meteostat
    city_info = WeatherDataLoader.get_city_info(city_name)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # 3. Query Meteostat
    location = Point(city_info['lat'], city_info['lon'])
    data = Daily(location, start_date, end_date)
    df = data.fetch()
    
    if df.empty:
        raise ValueError(f"No data available for {city_name}")
    
    # 4. Save to cache
    df.reset_index(inplace=True)
    df.rename(columns={'time': 'date'}, inplace=True)
    df.to_csv(cache_file, index=False)
    
    # 5. Return with date as index
    df.set_index('date', inplace=True)
    return df
```

**Cache Invalidation:**
```python
# Option 1: Manual clear in UI
if st.button("Refresh Data"):
    st.cache_data.clear()  # Clear all caches
    st.rerun()

# Option 2: Delete cache files
import os
for f in os.listdir('data/raw/'):
    os.remove(f'data/raw/{f}')

# Option 3: Wait for TTL expiry
# 30 min for real-time, 24 hours for historical
```

---

### 3. `utils/preprocessing.py` - Feature Engineering

**Purpose**: Clean data and create ML features

#### **Class Structure**
```python
class WeatherPreprocessor:
    def __init__(self):
        self.scaler = MinMaxScaler()
        
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values"""
        
    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Engineer features for ML models"""
        
    def prepare_for_prophet(self, df: pd.DataFrame) -> pd.DataFrame:
        """Format for Prophet (ds, y columns)"""
        
    def prepare_for_xgboost(self, df: pd.DataFrame, target: str) -> tuple:
        """Create X, y matrices for XGBoost"""
        
    def prepare_for_lstm(self, df: pd.DataFrame, lookback: int) -> tuple:
        """Create sequences for LSTM"""
```

#### **Feature Engineering**
```python
def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
    """
    Create ML features from raw weather data.
    
    Features created:
        - Lag features (1, 7, 30 days)
        - Rolling statistics (7-day window)
        - Cyclical date features (sin/cos)
    """
    df = df.copy()
    
    # 1. Lag features (previous values)
    for col in ['tavg', 'prcp', 'wspd']:
        df[f'{col}_lag_1'] = df[col].shift(1)    # Yesterday
        df[f'{col}_lag_7'] = df[col].shift(7)    # Last week
        df[f'{col}_lag_30'] = df[col].shift(30)  # Last month
    
    # 2. Rolling statistics (moving averages)
    for col in ['tavg', 'prcp']:
        df[f'{col}_rolling_7_mean'] = df[col].rolling(7).mean()
        df[f'{col}_rolling_7_std'] = df[col].rolling(7).std()
    
    # 3. Cyclical date features (capture seasonality)
    df['day_of_year'] = df.index.dayofyear
    df['day_of_year_sin'] = np.sin(2 * np.pi * df['day_of_year'] / 365)
    df['day_of_year_cos'] = np.cos(2 * np.pi * df['day_of_year'] / 365)
    
    df['month'] = df.index.month
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    
    # 4. Drop rows with NaN (from lag features)
    df.dropna(inplace=True)
    
    return df
```

**Why Cyclical Features?**
```python
# Problem: Month 12 and Month 1 should be close, but:
df['month'] = [1, 2, ..., 11, 12]  # 12 is far from 1 numerically

# Solution: Use sin/cos to make it circular
# December (12) and January (1) are now close
import numpy as np
month_sin = np.sin(2 * np.pi * month / 12)
month_cos = np.cos(2 * np.pi * month / 12)

# Visualization:
# Month:  1    2    3   ...  11   12    1
# Sin:  0.5  0.9  1.0  ... -0.9 -0.5  0.5  ← Smooth transition!
```

---

### 4. `pages/1_Dashboard.py` - Main Dashboard

**Purpose**: Display real-time weather and historical trends

#### **Page Structure**
```python
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data_loader import WeatherDataLoader
from utils.preprocessing import WeatherPreprocessor

# 1. Page config
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

# 2. Initialize loader (cached)
@st.cache_resource
def get_loader():
    return WeatherDataLoader()

loader = get_loader()

# 3. Sidebar - City selection
with st.sidebar:
    city_list = loader.get_city_list()
    selected_city = st.selectbox("Choose city", city_list)
    
    if st.button("Refresh"):
        st.cache_data.clear()
        st.rerun()

# 4. Load data (cached)
realtime = loader.get_realtime_weather(selected_city)
historical = loader.fetch_historical_data(selected_city, days=30)

# 5. Display real-time weather card
st.markdown("## 🌡️ Current Weather")
# ... weather card HTML/CSS

# 6. Display historical charts
st.markdown("## 📊 30-Day Trends")
tab1, tab2, tab3 = st.tabs(["Temperature", "Precipitation", "Wind"])

with tab1:
    # Temperature chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=historical.index, y=historical['tavg']))
    st.plotly_chart(fig, use_container_width=True)
```

#### **Real-Time Weather Card**
```python
# Get weather data
weather = loader.get_realtime_weather(selected_city)
emoji = loader.get_weather_emoji(weather['icon'])

# Create card with custom HTML/CSS
st.markdown(f"""
<div class="weather-card">
    <div style="text-align: center;">
        <div style="font-size: 80px;">{emoji}</div>
        <div style="font-size: 48px; font-weight: bold;">
            {weather['temperature']}°C
        </div>
        <div style="font-size: 24px; opacity: 0.9;">
            {weather['description']}
        </div>
    </div>
</div>

<style>
.weather-card {{
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 15px;
    padding: 30px;
    color: white;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    margin: 20px 0;
}}
</style>
""", unsafe_allow_html=True)
```

**Why `unsafe_allow_html=True`?**
- Allows custom CSS for styling
- Streamlit sanitizes to prevent XSS attacks
- Necessary for gradient backgrounds and custom layouts

#### **Interactive Charts**
```python
import plotly.graph_objects as go

# Temperature trends chart
fig = go.Figure()

# Add average temperature line
fig.add_trace(go.Scatter(
    x=df.index,
    y=df['tavg'],
    name='Avg Temp',
    line=dict(color='#FF6B6B', width=3),
    mode='lines'
))

# Add min/max range
fig.add_trace(go.Scatter(
    x=df.index,
    y=df['tmax'],
    name='Max',
    line=dict(color='#FFA500', width=2, dash='dot'),
    mode='lines'
))

fig.add_trace(go.Scatter(
    x=df.index,
    y=df['tmin'],
    name='Min',
    line=dict(color='#4ECDC4', width=2, dash='dot'),
    fill='tonexty',  # Fill between min and max
    fillcolor='rgba(78,205,196,0.2)',
    mode='lines'
))

# Customize layout
fig.update_layout(
    title='Temperature Trends (30 Days)',
    xaxis_title='Date',
    yaxis_title='Temperature (°C)',
    template='plotly_dark',
    hovermode='x unified',  # Show all values on hover
    height=400
)

# Display in Streamlit
st.plotly_chart(fig, use_container_width=True)
```

---

## Adding New Features

### Add a New City
```python
# In utils/data_loader.py, add to INDIAN_CITIES dict:
INDIAN_CITIES = {
    # ... existing cities
    'newcity': {
        'name': 'New City',
        'lat': 12.3456,
        'lon': 78.9012,
        'state': 'State Name'
    }
}
```

### Add a New Weather Parameter
```python
# 1. Update get_realtime_weather() in data_loader.py
return {
    # ... existing fields
    'uv_index': data.get('uvi', 0),  # Add UV index
}

# 2. Update display in 1_Dashboard.py
st.metric("UV Index", weather['uv_index'])
```

### Add a New Page
```python
# 1. Create pages/2_NewPage.py
import streamlit as st

st.set_page_config(page_title="New Page", page_icon="🆕", layout="wide")

st.title("🆕 New Feature Page")
# ... your content

# 2. That's it! Streamlit auto-creates navigation
```

---

## Common Tasks

### Task 1: Clear All Caches
```python
# In dashboard sidebar
if st.button("Clear Cache"):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.success("Cache cleared!")
    st.rerun()
```

### Task 2: Export Data to CSV
```python
# Add download button
csv = df.to_csv(index=True)
st.download_button(
    label="📥 Download Data",
    data=csv,
    file_name=f"{selected_city}_weather.csv",
    mime="text/csv"
)
```

### Task 3: Add Loading Spinner
```python
with st.spinner("Loading data..."):
    data = load_data(city)
    time.sleep(1)  # Optional delay
st.success("Data loaded!")
```

### Task 4: Debug Mode
```python
# Add to sidebar
debug_mode = st.sidebar.checkbox("Debug Mode")

if debug_mode:
    st.sidebar.write("Session State:", st.session_state)
    st.sidebar.write("Cache Info:", st.cache_data.get_stats())
    st.sidebar.json(weather_data)  # Show raw API response
```

---

## Debugging Guide

### Problem: "Module not found"
```bash
# Solution: Activate virtual environment
.\env\Scripts\activate  # Windows
source env/bin/activate  # Linux

# Verify packages
pip list | grep streamlit
```

### Problem: "API key invalid"
```python
# Debug: Print API key (remove before commit!)
import os
from dotenv import load_dotenv
load_dotenv()
print("API Key:", os.getenv('OPENWEATHERMAP_API_KEY'))

# Check:
# 1. .env file exists in project root
# 2. Key format: OPENWEATHERMAP_API_KEY=abc123... (no quotes)
# 3. Restart Streamlit after creating .env
```

### Problem: "Slow loading"
```python
# Debug: Check cache hits
@st.cache_data(ttl=1800)
def get_data(city):
    print(f"Cache miss! Fetching {city}")  # Only prints on cache miss
    return data

# Solution: Increase cache TTL
@st.cache_data(ttl=3600)  # 1 hour instead of 30 min
```

### Problem: "Data not refreshing"
```python
# Force refresh by clearing specific cache
import streamlit as st

# Clear specific function cache
get_realtime_weather.clear()

# Or clear all
st.cache_data.clear()
st.rerun()
```

### Problem: "Plotly chart not showing"
```python
# Debug: Check data
print(df.head())
print(df.dtypes)  # Ensure numeric types
print(df.isna().sum())  # Check for NaN

# Ensure use_container_width is set
st.plotly_chart(fig, use_container_width=True)
```

---

## Best Practices

### 1. Caching
```python
# ✅ DO: Cache expensive operations
@st.cache_data(ttl=1800)
def load_data(city):
    return pd.read_csv(...)

# ❌ DON'T: Cache user-specific data
@st.cache_data  # Bad! Will show wrong data to users
def get_user_preferences(user_id):
    return db.query(user_id)
```

### 2. Error Handling
```python
# ✅ DO: User-friendly errors
try:
    data = fetch_api()
except requests.Timeout:
    st.error("⏱️ Request timed out. Please try again.")
except Exception as e:
    st.error("❌ Something went wrong. Please refresh.")
    if st.checkbox("Show details"):
        st.exception(e)

# ❌ DON'T: Expose internals
st.error(str(exception))  # Shows stack trace to users
```

### 3. Performance
```python
# ✅ DO: Load data only when needed
if selected_city:
    data = load_data(selected_city)

# ❌ DON'T: Load all cities upfront
all_data = {city: load_data(city) for city in all_cities}  # Slow!
```

---

## Useful Streamlit Commands

### Session State (Persist Data)
```python
# Initialize
if 'counter' not in st.session_state:
    st.session_state.counter = 0

# Increment
if st.button("Increment"):
    st.session_state.counter += 1

# Display
st.write(f"Counter: {st.session_state.counter}")
```

### Custom Callbacks
```python
def on_city_change():
    st.session_state.data_loaded = False
    st.cache_data.clear()

city = st.selectbox(
    "City",
    options=cities,
    on_change=on_city_change  # Runs when selection changes
)
```

### Progress Bar
```python
import time

progress = st.progress(0)
for i in range(100):
    time.sleep(0.01)
    progress.progress(i + 1)
st.success("Complete!")
```

---

*Happy Coding! 🚀*
