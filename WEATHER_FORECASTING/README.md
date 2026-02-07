# Weather Forecast Web Application - India 🇮🇳

A **real-time weather dashboard** focused on Indian cities with educational ML forecasting models.

## ✨ Features

### 🌡️ Real-Time Weather
- **Live weather data** from OpenWeatherMap API
- **156+ Indian cities** including rain & snow destinations 🌧️❄️
- **Beautiful weather cards** with dynamic icons and emojis
- Current temperature, humidity, wind speed, pressure, visibility
- Updates every 30 minutes (auto-cached)

### 📊 Historical Data Analysis
- **Lightweight 30-day history** from Meteostat
- Interactive temperature, precipitation, and wind charts
- Daily trends and statistics
- Fast loading with local caching

### 🤖 ML Models (Coming Soon)
- **Prophet**: Seasonal trend decomposition
- **XGBoost**: Feature importance analysis  
- **LSTM**: Deep learning sequence prediction

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. (Optional) Add API Key
For **real live weather**, get a free API key:
1. Sign up at https://openweathermap.org/api
2. Create `.env` file with:
   ```
   OPENWEATHERMAP_API_KEY=your_key_here
   ```

**OR just run without it** - the app works fine with mock data!

### 3. Run the App
```bash
streamlit run app.py
```

Open http://localhost:8501 and go to **📊 Dashboard**!

## 🌍 Supported Cities

**156+ Indian Cities** including:
- **Metro Cities**: Mumbai, Delhi, Bangalore, Hyderabad, Chennai, Kolkata
- **Tier-1 Cities**: Pune, Ahmedabad, Jaipur, Lucknow, Kanpur, Surat, Nagpur
- **Hill Stations**: Shimla, Manali, Dharamshala, Nainital, Mussoorie, Ooty, Darjeeling
- **Tourist Destinations**: Goa, Leh, Srinagar, Munnar, Wayanad, Coorg
- **🌧️ Rain Paradise**: Cherrapunji, Mawsynram, Mahabaleshwar, Amboli, Coorg
- **❄️ Snow Destinations**: Gulmarg, Pahalgam, Auli, Kullu, Spiti, Kedarnath
- **State Capitals**: All state capitals and UT headquarters
- **Coastal Cities**: Kochi, Udupi, Karwar, Ratnagiri, Alibag, Mahabalipuram

*Full coverage across North, South, East, West, and Northeast India*

### Weather Icons
The app automatically displays weather-appropriate emojis:
- ☀️ Clear Sky | ⛅ Partly Cloudy | ☁️ Cloudy
- 🌧️ Rain | ⛈️ Thunderstorm | 🌫️ Mist
- ❄️ Snow | 🌦️ Light Rain

## 📁 Project Structure
```
├── app.py                   # Landing page
├── pages/
│   └── 1_Dashboard.py      # Real-time + historical dashboard
├── utils/
│   ├── data_loader.py      # Weather APIs integration
│   └── preprocessing.py    # Feature engineering
├── data/raw/               # Cached weather data
└── .env                    # API keys (create this)
```

## 🎓 Educational Purpose

This project demonstrates:
- **API Integration**: OpenWeatherMap + Meteostat
- **Data Caching**: Smart local storage
- **Interactive UI**: Streamlit multi-page apps
- **Data Visualization**: Plotly charts
- **ML Pipeline**: Feature engineering for forecasting

Perfect for data science portfolios!
