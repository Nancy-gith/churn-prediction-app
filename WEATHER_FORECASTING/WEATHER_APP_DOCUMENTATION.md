# 🌤️ Weather Application - Complete Documentation

## Overview

This Python application provides comprehensive weather analysis with:
- **Real-time weather data** from OpenWeatherMap API
- **30-day historical visualization** with color-coded trend graphs
- **CSV data export** for further analysis

---

## Features

### Part 1: Real-Time Weather Data
Displays current weather metrics including:
- ✅ Temperature (°C and °F)
- ✅ Humidity (%)
- ✅ Wind Speed (km/h and m/s)
- ✅ Atmospheric Pressure (hPa)
- ✅ Visibility (km)
- ✅ Cloud Cover (%)
- ✅ Latitude and Longitude
- ✅ Location name and country
- ✅ Weather description

### Part 2: 30-Day Historical Graphs

#### Graph 1: Temperature Trend 🌡️
- Daily temperature for past 30 days
- Min/Max range shaded area
- Trend line showing overall direction
- **Color Coding:**
  - 🔴 **RED**: Temperature increased
  - 🔵 **BLUE**: Temperature decreased
  - 🟡 **YELLOW**: Temperature stable (±0.5°C)

#### Graph 2: Precipitation Trend 🌧️
- Daily rainfall as bar chart
- 7-day moving average
- **Color Coding:**
  - 🔴 **RED**: Precipitation increased
  - 🔵 **BLUE**: Precipitation decreased
  - 🟡 **YELLOW**: Precipitation stable

#### Graph 3: Wind & Pressure Trend 💨🎚️
- Wind speed line graph (top)
- Atmospheric pressure line graph (bottom)
- **Color Coding:**
  - 🔴 **RED**: Value increased
  - 🔵 **BLUE**: Value decreased
  - 🟡 **YELLOW**: Value stable

---

## Installation

### Prerequisites
- Python 3.8 or higher
- Internet connection for API access

### Step 1: Install Dependencies
```bash
cd WEATHER_FORECASTING
pip install -r requirements.txt
```

Or install individually:
```bash
pip install requests pandas numpy matplotlib python-dotenv meteostat
```

### Step 2: Configure API Key (Optional)

**Without API key:** The app works with demo data - perfect for testing!

**With API key:** Get real-time data from OpenWeatherMap

1. Go to [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for free account
3. Go to API Keys section
4. Copy your API key
5. Create `.env` file:
```
OPENWEATHERMAP_API_KEY=your_actual_api_key_here
```

---

## Usage

### Run the Application
```bash
python weather_app_standalone.py
```

### Example Session
```
================================================================
🌤️  WEATHER APPLICATION - Real-Time Data & Historical Visualization  🌤️
================================================================
This application provides:
  • Real-time weather data from OpenWeatherMap
  • 30-day historical weather analysis
  • Color-coded trend graphs (Red/Blue/Yellow)
  • CSV data export
----------------------------------------------------------------

📍 Enter location (city name or lat,lon): New Delhi

🌤️  Fetching current weather data for 'New Delhi'...
✅ Successfully fetched weather data for New Delhi

============================================================
🌍 CURRENT WEATHER IN NEW DELHI, IN
============================================================
📅 Time: 2026-02-07 16:30:00
------------------------------------------------------------
🌡️  Temperature:    28.5°C (83.3°F)
🤒 Feels Like:     30.2°C (86.4°F)
💧 Humidity:       65%
💨 Wind Speed:     12.0 km/h (3.3 m/s)
🎚️  Pressure:       1013 hPa
👁️  Visibility:     10.0 km
☁️  Cloud Cover:    40%
📝 Conditions:     Partly Cloudy
📍 Coordinates:    28.6139°N, 77.2090°E
============================================================

📊 Fetching 30-day historical data...
✅ Successfully fetched 30 days of historical data from Meteostat

🔄 Processing daily changes...
✅ Daily changes processed successfully

📈 Generating Temperature Trend Graph...
✅ Temperature graph saved: weather_outputs/temperature_trend_30days.png

📈 Generating Precipitation Trend Graph...
✅ Precipitation graph saved: weather_outputs/precipitation_trend_30days.png

📈 Generating Wind Speed & Pressure Graph...
✅ Wind & Pressure graph saved: weather_outputs/wind_pressure_trend_30days.png

📄 Data exported to CSV: weather_outputs/weather_data_new_delhi_20260207.csv

======================================================================
✅ ALL TASKS COMPLETED SUCCESSFULLY!
======================================================================

📊 OUTPUT FILES GENERATED:
   1. weather_outputs/temperature_trend_30days.png
   2. weather_outputs/precipitation_trend_30days.png
   3. weather_outputs/wind_pressure_trend_30days.png
   4. weather_outputs/weather_data_new_delhi_20260207.csv

📁 All files saved in: C:\Users\NANCY\...\WEATHER_FORECASTING\weather_outputs
======================================================================

🖼️  Would you like to display the graphs? (y/n): y
Opening graphs in viewer...
```

---

## Output Files

All outputs are saved in the `weather_outputs/` folder:

| File | Description |
|------|-------------|
| `temperature_trend_30days.png` | Temperature graph with color coding |
| `precipitation_trend_30days.png` | Rainfall bar chart with color coding |
| `wind_pressure_trend_30days.png` | Combined wind & pressure graphs |
| `weather_data_*.csv` | Raw data for further analysis |

---

## Color Coding Logic

### Tolerance Settings
- **Temperature**: ±0.5°C tolerance for "stable"
- **Precipitation**: ±0.5mm tolerance for "stable"
- **Wind Speed**: ±0.5 km/h tolerance for "stable"
- **Pressure**: ±2 hPa tolerance for "stable"

### Color Meanings
| Color | Meaning | Condition |
|-------|---------|-----------|
| 🔴 RED | Increased | Current > Previous + tolerance |
| 🔵 BLUE | Decreased | Current < Previous - tolerance |
| 🟡 YELLOW | Stable | Within ±tolerance |

### Example:
- Day 1: 25°C
- Day 2: 26°C → RED (increased by 1°C, > 0.5°C tolerance)
- Day 3: 25.8°C → YELLOW (decreased by 0.2°C, within tolerance)
- Day 4: 24°C → BLUE (decreased by 1.8°C, > 0.5°C tolerance)

---

## Data Sources

### Real-Time Weather
- **Primary**: OpenWeatherMap API (with API key)
- **Fallback**: Demo data (without API key)

### Historical Weather
- **Primary**: Meteostat library (FREE, no API key needed!)
- **Fallback**: Synthetic data based on climate patterns

---

## Code Structure

```
weather_app_standalone.py
│
├── CONFIGURATION
│   └── API keys, colors, output paths
│
├── UTILITY FUNCTIONS
│   ├── celsius_to_fahrenheit()
│   ├── get_comparison_color()
│   └── format_coordinates()
│
├── PART 1: REAL-TIME DATA
│   ├── fetch_current_weather()
│   ├── _get_demo_current_weather()
│   └── display_current_weather()
│
├── PART 2: HISTORICAL DATA
│   ├── fetch_historical_data()
│   ├── _fetch_from_meteostat()
│   ├── _generate_synthetic_history()
│   └── process_daily_changes()
│
├── PART 3: VISUALIZATIONS
│   ├── create_temperature_graph()
│   ├── create_precipitation_graph()
│   └── create_wind_pressure_graph()
│
├── DATA EXPORT
│   └── export_to_csv()
│
└── MAIN
    └── main() - Orchestrates all functions
```

---

## Error Handling

### API Errors
| Error | Message | Solution |
|-------|---------|----------|
| 401 | Invalid API key | Check your API key in `.env` |
| 404 | Location not found | Verify city spelling |
| 429 | Rate limit exceeded | Wait and try again |
| Timeout | Connection timed out | Check internet connection |

### Fallback Behavior
- No API key → Uses demo data
- No Meteostat data → Generates synthetic historical data
- API error → Falls back to demo data

---

## Customization

### Change Colors
Edit the COLORS dictionary:
```python
COLORS = {
    'increase': '#E74C3C',   # Red
    'decrease': '#3498DB',   # Blue
    'stable': '#F1C40F',     # Yellow
}
```

### Change Tolerance
```python
TOLERANCE = 0.5  # ±0.5 units for "stable" comparison
```

### Change Output Directory
```python
OUTPUT_DIR = "my_custom_folder"
```

---

## Graph Features

### Temperature Graph
- Colored line segments connecting days
- Colored markers at each data point
- Dashed trend line (linear regression)
- Min-Max temperature range shading
- Statistics box (Average, Max, Min)

### Precipitation Graph
- Colored bar chart for each day
- Value labels for significant rainfall (>5mm)
- 7-day moving average line
- Total rainfall and rainy days count

### Wind & Pressure Graph
- Two subplots (Wind on top, Pressure below)
- Colored line segments and markers
- Trend lines for each
- Statistics annotations

---

## CSV Export Format

The exported CSV includes:
| Column | Description | Unit |
|--------|-------------|------|
| date | Date of measurement | YYYY-MM-DD |
| temperature | Average temperature | °C |
| temp_min | Minimum temperature | °C |
| temp_max | Maximum temperature | °C |
| precipitation | Daily rainfall | mm |
| wind_speed | Average wind speed | km/h |
| pressure | Atmospheric pressure | hPa |

---

## Troubleshooting

### "No module named 'meteostat'"
```bash
pip install meteostat
```

### "API key not working"
1. Check if key is correct in `.env`
2. Ensure no quotes around the key
3. Wait a few minutes (new keys take time to activate)

### "No historical data available"
- Some remote locations may not have weather stations
- App automatically generates synthetic data as fallback

### "Graphs not displaying"
- Ensure matplotlib is installed: `pip install matplotlib`
- Check the `weather_outputs/` folder for saved PNG files

---

## Support

For issues or questions:
1. Check documentation above
2. Look at error messages for hints
3. Verify all dependencies are installed
4. Try a different city/location

---

## License

This project is for educational purposes. Weather data is provided by:
- OpenWeatherMap (requires free API key for live data)
- Meteostat (free, open source)

---

*Happy Weather Tracking!* 🌤️📊
