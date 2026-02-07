"""
===============================================================================
WEATHER APPLICATION - Real-Time Data & Historical Visualization
===============================================================================
A comprehensive Python application for weather analysis with:
- Real-time weather data retrieval from OpenWeatherMap API
- 30-day historical weather visualization
- Color-coded trend graphs (Red=Increase, Blue=Decrease, Yellow=Same)
- CSV export functionality
- Interactive and saved graph outputs

Author: Weather Forecasting Project
Version: 1.0
===============================================================================
"""

# ============================================================================
# IMPORTS
# ============================================================================
import os
import sys

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')

import json
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.collections import LineCollection
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

# API Configuration
OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY', '')

# API Endpoints
CURRENT_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
HISTORICAL_URL = "https://api.openweathermap.org/data/2.5/onecall/timemachine"  # Premium

# Meteostat for free historical data (alternative)
USE_METEOSTAT = True  # Set to True to use Meteostat (free, no API key needed)

# Output Configuration
OUTPUT_DIR = "weather_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Color Configuration (accessible, colorblind-friendly)
COLORS = {
    'increase': '#E74C3C',   # Red - Temperature/value increased
    'decrease': '#3498DB',   # Blue - Temperature/value decreased  
    'stable': '#F1C40F',     # Yellow - Value remained stable
    'line': '#2C3E50',       # Dark gray - Main line color
    'grid': '#BDC3C7',       # Light gray - Grid lines
    'background': '#FAFAFA'  # Off-white background
}

# Tolerance for "same" comparison
TOLERANCE = 0.5  # ±0.5 units (°C, mm, km/h)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert Celsius to Fahrenheit."""
    return (celsius * 9/5) + 32


def get_comparison_color(current: float, previous: float, tolerance: float = TOLERANCE) -> str:
    """
    Compare current value with previous and return appropriate color.
    
    Args:
        current: Current day's value
        previous: Previous day's value
        tolerance: Range for considering values as "same"
    
    Returns:
        Color code (hex string)
    """
    difference = current - previous
    
    if difference > tolerance:
        return COLORS['increase']  # Red - Increased
    elif difference < -tolerance:
        return COLORS['decrease']  # Blue - Decreased
    else:
        return COLORS['stable']    # Yellow - Same


def format_coordinates(lat: float, lon: float) -> str:
    """Format coordinates with N/S and E/W indicators."""
    lat_dir = 'N' if lat >= 0 else 'S'
    lon_dir = 'E' if lon >= 0 else 'W'
    return f"{abs(lat):.4f}°{lat_dir}, {abs(lon):.4f}°{lon_dir}"


# ============================================================================
# PART 1: REAL-TIME WEATHER DATA RETRIEVAL
# ============================================================================

def fetch_current_weather(location: str) -> dict:
    """
    Fetch current weather data from OpenWeatherMap API.
    
    Args:
        location: City name (e.g., "New Delhi") or coordinates ("lat,lon")
    
    Returns:
        Dictionary containing current weather metrics
    
    Raises:
        Exception: If API call fails or location not found
    """
    print(f"\n🌤️  Fetching current weather data for '{location}'...")
    
    # Check if API key is configured
    if not OPENWEATHERMAP_API_KEY or OPENWEATHERMAP_API_KEY == 'your_api_key_here':
        print("⚠️  No API key configured. Using demo data...")
        return _get_demo_current_weather(location)
    
    try:
        # Build API request parameters
        params = {
            'appid': OPENWEATHERMAP_API_KEY,
            'units': 'metric',  # Celsius
        }
        
        # Check if location is coordinates or city name
        if ',' in location and location.replace(',', '').replace('.', '').replace('-', '').replace(' ', '').isdigit():
            lat, lon = map(float, location.split(','))
            params['lat'] = lat
            params['lon'] = lon
        else:
            params['q'] = location
        
        # Make API request
        response = requests.get(CURRENT_WEATHER_URL, params=params, timeout=10)
        
        # Handle HTTP errors
        if response.status_code == 401:
            raise Exception("Invalid API key. Please check your OpenWeatherMap API key.")
        elif response.status_code == 404:
            raise Exception(f"Location '{location}' not found. Please check the city name.")
        elif response.status_code == 429:
            raise Exception("API rate limit exceeded. Please try again later.")
        
        response.raise_for_status()
        data = response.json()
        
        # Extract and format weather data
        weather_data = {
            'location': data['name'],
            'country': data['sys']['country'],
            'temperature_c': round(data['main']['temp'], 1),
            'temperature_f': round(celsius_to_fahrenheit(data['main']['temp']), 1),
            'feels_like_c': round(data['main']['feels_like'], 1),
            'feels_like_f': round(celsius_to_fahrenheit(data['main']['feels_like']), 1),
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'wind_speed_ms': round(data['wind']['speed'], 1),
            'wind_speed_kmh': round(data['wind']['speed'] * 3.6, 1),  # m/s to km/h
            'visibility_m': data.get('visibility', 10000),
            'visibility_km': round(data.get('visibility', 10000) / 1000, 1),
            'cloud_cover': data['clouds']['all'],
            'latitude': data['coord']['lat'],
            'longitude': data['coord']['lon'],
            'description': data['weather'][0]['description'].title(),
            'icon': data['weather'][0]['icon'],
            'timestamp': datetime.fromtimestamp(data['dt'])
        }
        
        print(f"✅ Successfully fetched weather data for {weather_data['location']}")
        return weather_data
        
    except requests.Timeout:
        raise Exception("Connection timed out. Please check your internet connection.")
    except requests.ConnectionError:
        raise Exception("Could not connect to weather service. Please check your internet connection.")
    except Exception as e:
        if "Invalid API key" in str(e) or "not found" in str(e):
            raise
        print(f"⚠️  API error: {e}. Using demo data...")
        return _get_demo_current_weather(location)


def _get_demo_current_weather(location: str) -> dict:
    """Generate demo current weather data when API is unavailable."""
    import random
    
    # Common Indian cities with approximate coordinates
    cities = {
        'new delhi': {'lat': 28.6139, 'lon': 77.2090, 'country': 'IN'},
        'delhi': {'lat': 28.6139, 'lon': 77.2090, 'country': 'IN'},
        'mumbai': {'lat': 19.0760, 'lon': 72.8777, 'country': 'IN'},
        'bangalore': {'lat': 12.9716, 'lon': 77.5946, 'country': 'IN'},
        'chennai': {'lat': 13.0827, 'lon': 80.2707, 'country': 'IN'},
        'kolkata': {'lat': 22.5726, 'lon': 88.3639, 'country': 'IN'},
        'hyderabad': {'lat': 17.3850, 'lon': 78.4867, 'country': 'IN'},
        'dehradun': {'lat': 30.3165, 'lon': 78.0322, 'country': 'IN'},
        'shimla': {'lat': 31.1048, 'lon': 77.1734, 'country': 'IN'},
        'jaipur': {'lat': 26.9124, 'lon': 75.7873, 'country': 'IN'},
    }
    
    location_key = location.lower().strip()
    city_info = cities.get(location_key, {'lat': 28.6139, 'lon': 77.2090, 'country': 'IN'})
    
    # Generate realistic temperature based on location
    base_temp = 25 + random.uniform(-5, 10)
    
    return {
        'location': location.title(),
        'country': city_info['country'],
        'temperature_c': round(base_temp, 1),
        'temperature_f': round(celsius_to_fahrenheit(base_temp), 1),
        'feels_like_c': round(base_temp + random.uniform(-2, 2), 1),
        'feels_like_f': round(celsius_to_fahrenheit(base_temp + 1), 1),
        'humidity': random.randint(40, 80),
        'pressure': random.randint(1008, 1018),
        'wind_speed_ms': round(random.uniform(2, 8), 1),
        'wind_speed_kmh': round(random.uniform(7, 30), 1),
        'visibility_m': 10000,
        'visibility_km': 10.0,
        'cloud_cover': random.randint(10, 60),
        'latitude': city_info['lat'],
        'longitude': city_info['lon'],
        'description': random.choice(['Clear Sky', 'Partly Cloudy', 'Scattered Clouds', 'Haze']),
        'icon': '01d',
        'timestamp': datetime.now()
    }


def display_current_weather(weather: dict) -> None:
    """
    Display current weather data in a clean, formatted output.
    
    Args:
        weather: Dictionary containing weather data
    """
    print("\n" + "=" * 60)
    print(f"🌍 CURRENT WEATHER IN {weather['location'].upper()}, {weather['country']}")
    print("=" * 60)
    print(f"📅 Time: {weather['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    print(f"🌡️  Temperature:    {weather['temperature_c']}°C ({weather['temperature_f']}°F)")
    print(f"🤒 Feels Like:     {weather['feels_like_c']}°C ({weather['feels_like_f']}°F)")
    print(f"💧 Humidity:       {weather['humidity']}%")
    print(f"💨 Wind Speed:     {weather['wind_speed_kmh']} km/h ({weather['wind_speed_ms']} m/s)")
    print(f"🎚️  Pressure:       {weather['pressure']} hPa")
    print(f"👁️  Visibility:     {weather['visibility_km']} km")
    print(f"☁️  Cloud Cover:    {weather['cloud_cover']}%")
    print(f"📝 Conditions:     {weather['description']}")
    print(f"📍 Coordinates:    {format_coordinates(weather['latitude'], weather['longitude'])}")
    print("=" * 60)


# ============================================================================
# PART 2: 30-DAY HISTORICAL WEATHER DATA
# ============================================================================

def fetch_historical_data(lat: float, lon: float, days: int = 30) -> pd.DataFrame:
    """
    Fetch historical weather data for the past N days.
    Uses Meteostat library for free historical data.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
        days: Number of days of historical data (default 30)
    
    Returns:
        DataFrame with historical weather data
    """
    print(f"\n📊 Fetching {days}-day historical data...")
    
    try:
        if USE_METEOSTAT:
            return _fetch_from_meteostat(lat, lon, days)
        else:
            return _fetch_from_openweathermap(lat, lon, days)
    except Exception as e:
        print(f"⚠️  Could not fetch historical data: {e}")
        print("📊 Generating synthetic historical data for demonstration...")
        return _generate_synthetic_history(lat, lon, days)


def _fetch_from_meteostat(lat: float, lon: float, days: int) -> pd.DataFrame:
    """Fetch historical data from Meteostat (free, no API key needed)."""
    try:
        from meteostat import Point, Daily
        
        # Create location point
        location = Point(lat, lon)
        
        # Define date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Fetch daily data
        data = Daily(location, start_date, end_date)
        df = data.fetch()
        
        if df.empty:
            # Try nearby location
            for offset in [0.5, 1.0, -0.5, -1.0]:
                location_nearby = Point(lat + offset, lon + offset)
                data = Daily(location_nearby, start_date, end_date)
                df = data.fetch()
                if not df.empty:
                    break
        
        if df.empty:
            raise Exception("No Meteostat data available for this location")
        
        # Reset index to include date column
        df = df.reset_index()
        df.columns = ['date' if col == 'time' else col for col in df.columns]
        
        # Rename columns for consistency
        df = df.rename(columns={
            'tavg': 'temperature',
            'tmin': 'temp_min',
            'tmax': 'temp_max',
            'prcp': 'precipitation',
            'wspd': 'wind_speed',
            'pres': 'pressure'
        })
        
        # Fill missing values properly
        # Precipitation: NaN means no rain, so fill with 0
        if 'precipitation' in df.columns:
            df['precipitation'] = df['precipitation'].fillna(0)
        
        # Temperature: interpolate missing values
        for col in ['temperature', 'temp_min', 'temp_max']:
            if col in df.columns:
                df[col] = df[col].ffill().bfill()
                # If still NaN, use a default
                df[col] = df[col].fillna(25.0)
        
        # Wind and pressure: forward fill then backward fill
        for col in ['wind_speed', 'pressure']:
            if col in df.columns:
                df[col] = df[col].ffill().bfill()
                df[col] = df[col].fillna(df[col].mean() if df[col].notna().any() else 10.0 if col == 'wind_speed' else 1013.0)
        
        print(f"✅ Successfully fetched {len(df)} days of historical data from Meteostat")
        return df
        
    except ImportError:
        print("⚠️  Meteostat not installed. Using synthetic data...")
        return _generate_synthetic_history(lat, lon, days)
    except Exception as e:
        print(f"⚠️  Meteostat error: {e}")
        return _generate_synthetic_history(lat, lon, days)


def _fetch_from_openweathermap(lat: float, lon: float, days: int) -> pd.DataFrame:
    """Fetch historical data from OpenWeatherMap (requires subscription)."""
    # OpenWeatherMap historical data requires paid subscription
    # This function is a placeholder for when premium access is available
    print("⚠️  OpenWeatherMap historical data requires premium subscription")
    return _generate_synthetic_history(lat, lon, days)


def _generate_synthetic_history(lat: float, lon: float, days: int) -> pd.DataFrame:
    """
    Generate realistic synthetic historical data for demonstration.
    Uses latitude-based climate patterns and seasonal variations.
    """
    np.random.seed(42)  # For reproducibility
    
    # Determine climate zone based on latitude
    if lat > 30:  # Hill stations
        base_temp = 18
        temp_variation = 8
    elif lat > 25:
        base_temp = 25
        temp_variation = 10
    elif lat > 20:
        base_temp = 28
        temp_variation = 6
    else:
        base_temp = 27
        temp_variation = 5
    
    # Generate dates
    end_date = datetime.now()
    dates = [end_date - timedelta(days=i) for i in range(days-1, -1, -1)]
    
    # Generate realistic temperature with trends
    day_of_year = np.array([d.timetuple().tm_yday for d in dates])
    seasonal = np.sin(2 * np.pi * (day_of_year - 80) / 365) * temp_variation
    random_walk = np.cumsum(np.random.normal(0, 0.5, days))
    random_walk = random_walk - random_walk.mean()  # Center around zero
    
    temperature = base_temp + seasonal + np.random.normal(0, 2, days) + random_walk * 0.3
    temp_min = temperature - np.random.uniform(3, 6, days)
    temp_max = temperature + np.random.uniform(3, 6, days)
    
    # Generate precipitation (monsoon-aware)
    month = np.array([d.month for d in dates])
    monsoon_factor = np.where((month >= 6) & (month <= 9), 2.0, 0.3)
    precipitation = np.random.exponential(3, days) * monsoon_factor
    precipitation = np.clip(precipitation, 0, 50)  # Realistic limits
    
    # Generate wind speed
    wind_speed = np.random.uniform(5, 20, days) + np.random.normal(0, 3, days)
    wind_speed = np.clip(wind_speed, 2, 40)
    
    # Generate pressure
    pressure = np.random.normal(1013, 5, days)
    
    df = pd.DataFrame({
        'date': dates,
        'temperature': np.round(temperature, 1),
        'temp_min': np.round(temp_min, 1),
        'temp_max': np.round(temp_max, 1),
        'precipitation': np.round(precipitation, 1),
        'wind_speed': np.round(wind_speed, 1),
        'pressure': np.round(pressure, 1)
    })
    
    print(f"✅ Generated {len(df)} days of synthetic historical data")
    return df


def process_daily_changes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process historical data to compute daily changes and assign colors.
    
    Args:
        df: DataFrame with historical weather data
    
    Returns:
        DataFrame with added columns for changes and colors
    """
    print("\n🔄 Processing daily changes...")
    
    df = df.copy()
    
    # Calculate daily changes
    df['temp_change'] = df['temperature'].diff()
    df['precip_change'] = df['precipitation'].diff()
    df['wind_change'] = df['wind_speed'].diff()
    df['pressure_change'] = df['pressure'].diff()
    
    # Assign colors based on changes
    df['temp_color'] = df['temp_change'].apply(
        lambda x: COLORS['increase'] if x > TOLERANCE 
                  else COLORS['decrease'] if x < -TOLERANCE 
                  else COLORS['stable']
    )
    
    df['precip_color'] = df['precip_change'].apply(
        lambda x: COLORS['increase'] if x > TOLERANCE 
                  else COLORS['decrease'] if x < -TOLERANCE 
                  else COLORS['stable']
    )
    
    df['wind_color'] = df['wind_change'].apply(
        lambda x: COLORS['increase'] if x > TOLERANCE 
                  else COLORS['decrease'] if x < -TOLERANCE 
                  else COLORS['stable']
    )
    
    df['pressure_color'] = df['pressure_change'].apply(
        lambda x: COLORS['increase'] if x > 2 
                  else COLORS['decrease'] if x < -2 
                  else COLORS['stable']
    )
    
    # Fill first row with stable color (no previous day to compare)
    df.iloc[0, df.columns.get_loc('temp_color')] = COLORS['stable']
    df.iloc[0, df.columns.get_loc('precip_color')] = COLORS['stable']
    df.iloc[0, df.columns.get_loc('wind_color')] = COLORS['stable']
    df.iloc[0, df.columns.get_loc('pressure_color')] = COLORS['stable']
    
    print("✅ Daily changes processed successfully")
    return df


# ============================================================================
# PART 3: GRAPH GENERATION
# ============================================================================

def create_temperature_graph(df: pd.DataFrame, location: str, save_path: str = None) -> str:
    """
    GRAPH 1: Temperature Trend with Color Coding
    
    - RED: Temperature increased compared to previous day
    - BLUE: Temperature decreased compared to previous day
    - YELLOW: Temperature remained the same (±0.5°C)
    
    Args:
        df: DataFrame with historical data
        location: Location name for title
        save_path: Optional custom save path
    
    Returns:
        Path to saved graph image
    """
    print("\n📈 Generating Temperature Trend Graph...")
    
    fig, ax = plt.subplots(figsize=(14, 7), facecolor=COLORS['background'])
    ax.set_facecolor(COLORS['background'])
    
    dates = pd.to_datetime(df['date'])
    temps = df['temperature'].values
    colors = df['temp_color'].values
    
    # Plot line segments with colors
    for i in range(1, len(dates)):
        ax.plot([dates.iloc[i-1], dates.iloc[i]], 
                [temps[i-1], temps[i]], 
                color=colors[i], 
                linewidth=2.5, 
                solid_capstyle='round')
    
    # Plot colored markers
    for i in range(len(dates)):
        ax.scatter(dates.iloc[i], temps[i], 
                   color=colors[i], 
                   s=80, 
                   zorder=5,
                   edgecolors='white',
                   linewidths=1.5)
    
    # Add trend line
    z = np.polyfit(range(len(dates)), temps, 1)
    p = np.poly1d(z)
    ax.plot(dates, p(range(len(dates))), 
            '--', 
            color=COLORS['line'], 
            alpha=0.7, 
            linewidth=2,
            label=f'Trend ({z[0]:+.2f}°C/day)')
    
    # Add min/max bands if available
    if 'temp_min' in df.columns and 'temp_max' in df.columns:
        ax.fill_between(dates, 
                        df['temp_min'], 
                        df['temp_max'], 
                        alpha=0.15, 
                        color=COLORS['line'],
                        label='Min-Max Range')
    
    # Styling
    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_ylabel('Temperature (°C)', fontsize=12, fontweight='bold')
    ax.set_title(f'🌡️ 30-Day Temperature Trend - {location}\n'
                 f'RED = Increased | BLUE = Decreased | YELLOW = Stable',
                 fontsize=14, fontweight='bold', pad=20)
    
    ax.grid(True, alpha=0.3, color=COLORS['grid'])
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
    plt.xticks(rotation=45)
    
    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=COLORS['increase'], label='Temperature Increased'),
        Patch(facecolor=COLORS['decrease'], label='Temperature Decreased'),
        Patch(facecolor=COLORS['stable'], label='Temperature Stable (±0.5°C)')
    ]
    ax.legend(handles=legend_elements, loc='upper right', framealpha=0.9)
    
    # Add statistics annotation
    stats_text = f"Avg: {temps.mean():.1f}°C | Max: {temps.max():.1f}°C | Min: {temps.min():.1f}°C"
    ax.annotate(stats_text, xy=(0.02, 0.98), xycoords='axes fraction',
                fontsize=10, va='top', ha='left',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    
    # Save graph
    filepath = save_path or os.path.join(OUTPUT_DIR, 'temperature_trend_30days.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=COLORS['background'])
    print(f"✅ Temperature graph saved: {filepath}")
    
    plt.close()
    return filepath


def create_precipitation_graph(df: pd.DataFrame, location: str, save_path: str = None) -> str:
    """
    GRAPH 2: Precipitation Trend with Color Coding
    
    - RED: Precipitation increased compared to previous day
    - BLUE: Precipitation decreased compared to previous day
    - YELLOW: Precipitation remained the same
    
    Args:
        df: DataFrame with historical data
        location: Location name for title
        save_path: Optional custom save path
    
    Returns:
        Path to saved graph image
    """
    print("\n📈 Generating Precipitation Trend Graph...")
    
    fig, ax = plt.subplots(figsize=(14, 7), facecolor=COLORS['background'])
    ax.set_facecolor(COLORS['background'])
    
    dates = pd.to_datetime(df['date'])
    precip = df['precipitation'].values
    colors = df['precip_color'].values
    
    # Create bar chart with individual colors
    bars = ax.bar(dates, precip, 
                  color=colors, 
                  width=0.8,
                  edgecolor='white',
                  linewidth=0.5)
    
    # Add value labels on bars (only for significant rainfall)
    for i, (bar, val) in enumerate(zip(bars, precip)):
        if val > 5:  # Only label significant rainfall
            ax.annotate(f'{val:.1f}',
                        xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                        xytext=(0, 3),
                        textcoords='offset points',
                        ha='center',
                        va='bottom',
                        fontsize=8,
                        color=COLORS['line'])
    
    # Add moving average line
    window = min(7, len(df))
    moving_avg = pd.Series(precip).rolling(window=window, min_periods=1).mean()
    ax.plot(dates, moving_avg, 
            color=COLORS['line'], 
            linewidth=2,
            linestyle='--',
            label=f'{window}-Day Moving Avg')
    
    # Styling
    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_ylabel('Precipitation (mm)', fontsize=12, fontweight='bold')
    ax.set_title(f'🌧️ 30-Day Precipitation Trend - {location}\n'
                 f'RED = Increased | BLUE = Decreased | YELLOW = Stable',
                 fontsize=14, fontweight='bold', pad=20)
    
    ax.grid(True, alpha=0.3, color=COLORS['grid'], axis='y')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
    plt.xticks(rotation=45)
    
    # Set y-axis minimum to 0
    ax.set_ylim(bottom=0)
    
    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=COLORS['increase'], label='Precipitation Increased'),
        Patch(facecolor=COLORS['decrease'], label='Precipitation Decreased'),
        Patch(facecolor=COLORS['stable'], label='Precipitation Stable'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', framealpha=0.9)
    
    # Add statistics
    total_precip = precip.sum()
    rainy_days = (precip > 0.1).sum()
    stats_text = f"Total: {total_precip:.1f} mm | Rainy Days: {rainy_days}/{len(df)}"
    ax.annotate(stats_text, xy=(0.02, 0.98), xycoords='axes fraction',
                fontsize=10, va='top', ha='left',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    
    # Save graph
    filepath = save_path or os.path.join(OUTPUT_DIR, 'precipitation_trend_30days.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=COLORS['background'])
    print(f"✅ Precipitation graph saved: {filepath}")
    
    plt.close()
    return filepath


def create_wind_pressure_graph(df: pd.DataFrame, location: str, save_path: str = None) -> str:
    """
    GRAPH 3: Wind Speed & Pressure Trend with Color Coding
    
    - RED: Value increased compared to previous day
    - BLUE: Value decreased compared to previous day
    - YELLOW: Value remained stable
    
    Args:
        df: DataFrame with historical data
        location: Location name for title
        save_path: Optional custom save path
    
    Returns:
        Path to saved graph image
    """
    print("\n📈 Generating Wind Speed & Pressure Graph...")
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), facecolor=COLORS['background'])
    
    dates = pd.to_datetime(df['date'])
    
    # ---- WIND SPEED (Top subplot) ----
    ax1.set_facecolor(COLORS['background'])
    wind = df['wind_speed'].values
    wind_colors = df['wind_color'].values
    
    # Plot line segments with colors
    for i in range(1, len(dates)):
        ax1.plot([dates.iloc[i-1], dates.iloc[i]], 
                [wind[i-1], wind[i]], 
                color=wind_colors[i], 
                linewidth=2.5)
    
    # Colored markers
    for i in range(len(dates)):
        ax1.scatter(dates.iloc[i], wind[i], 
                   color=wind_colors[i], 
                   s=60, 
                   zorder=5,
                   edgecolors='white',
                   linewidths=1)
    
    # Add trend line
    z = np.polyfit(range(len(dates)), wind, 1)
    p = np.poly1d(z)
    ax1.plot(dates, p(range(len(dates))), 
            '--', color=COLORS['line'], alpha=0.7, linewidth=2)
    
    ax1.set_xlabel('Date', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Wind Speed (km/h)', fontsize=11, fontweight='bold')
    ax1.set_title(f'💨 Wind Speed Trend\n'
                  f'RED = Increased | BLUE = Decreased | YELLOW = Stable',
                  fontsize=12, fontweight='bold', pad=10)
    ax1.grid(True, alpha=0.3, color=COLORS['grid'])
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=5))
    
    # Wind stats
    ax1.annotate(f"Avg: {wind.mean():.1f} km/h | Max: {wind.max():.1f} km/h",
                xy=(0.02, 0.95), xycoords='axes fraction',
                fontsize=9, va='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # ---- PRESSURE (Bottom subplot) ----
    ax2.set_facecolor(COLORS['background'])
    pressure = df['pressure'].values
    pressure_colors = df['pressure_color'].values
    
    # Plot line segments with colors
    for i in range(1, len(dates)):
        ax2.plot([dates.iloc[i-1], dates.iloc[i]], 
                [pressure[i-1], pressure[i]], 
                color=pressure_colors[i], 
                linewidth=2.5)
    
    # Colored markers
    for i in range(len(dates)):
        ax2.scatter(dates.iloc[i], pressure[i], 
                   color=pressure_colors[i], 
                   s=60, 
                   zorder=5,
                   edgecolors='white',
                   linewidths=1)
    
    # Add trend line
    z = np.polyfit(range(len(dates)), pressure, 1)
    p = np.poly1d(z)
    ax2.plot(dates, p(range(len(dates))), 
            '--', color=COLORS['line'], alpha=0.7, linewidth=2)
    
    ax2.set_xlabel('Date', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Pressure (hPa)', fontsize=11, fontweight='bold')
    ax2.set_title(f'🎚️ Atmospheric Pressure Trend\n'
                  f'RED = Increased | BLUE = Decreased | YELLOW = Stable',
                  fontsize=12, fontweight='bold', pad=10)
    ax2.grid(True, alpha=0.3, color=COLORS['grid'])
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
    ax2.xaxis.set_major_locator(mdates.DayLocator(interval=5))
    
    # Pressure stats
    ax2.annotate(f"Avg: {pressure.mean():.1f} hPa | Range: {pressure.max()-pressure.min():.1f} hPa",
                xy=(0.02, 0.95), xycoords='axes fraction',
                fontsize=9, va='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Overall title
    fig.suptitle(f'🌀 30-Day Wind & Pressure Analysis - {location}',
                 fontsize=14, fontweight='bold', y=1.02)
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=COLORS['increase'], label='Increased'),
        Patch(facecolor=COLORS['decrease'], label='Decreased'),
        Patch(facecolor=COLORS['stable'], label='Stable')
    ]
    fig.legend(handles=legend_elements, loc='upper center', 
               ncol=3, bbox_to_anchor=(0.5, 1.01), framealpha=0.9)
    
    plt.tight_layout()
    
    # Save graph
    filepath = save_path or os.path.join(OUTPUT_DIR, 'wind_pressure_trend_30days.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=COLORS['background'])
    print(f"✅ Wind & Pressure graph saved: {filepath}")
    
    plt.close()
    return filepath


# ============================================================================
# DATA EXPORT
# ============================================================================

def export_to_csv(df: pd.DataFrame, location: str) -> str:
    """
    Export historical weather data to CSV file.
    
    Args:
        df: DataFrame with weather data
        location: Location name for filename
    
    Returns:
        Path to saved CSV file
    """
    # Clean location name for filename
    clean_location = location.lower().replace(' ', '_').replace(',', '')
    filename = f"weather_data_{clean_location}_{datetime.now().strftime('%Y%m%d')}.csv"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Select relevant columns
    export_columns = ['date', 'temperature', 'temp_min', 'temp_max', 
                      'precipitation', 'wind_speed', 'pressure']
    export_df = df[[col for col in export_columns if col in df.columns]].copy()
    
    # Save to CSV
    export_df.to_csv(filepath, index=False)
    print(f"📄 Data exported to CSV: {filepath}")
    
    return filepath


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """
    Main function to orchestrate the weather application workflow.
    
    Steps:
    1. Get location from user input
    2. Fetch current weather data
    3. Display current weather
    4. Fetch 30-day historical data
    5. Process daily changes
    6. Generate all three graphs
    7. Export data to CSV
    """
    print("\n" + "=" * 70)
    print("🌤️  WEATHER APPLICATION - Real-Time Data & Historical Visualization  🌤️")
    print("=" * 70)
    print("This application provides:")
    print("  • Real-time weather data from OpenWeatherMap")
    print("  • 30-day historical weather analysis")
    print("  • Color-coded trend graphs (Red/Blue/Yellow)")
    print("  • CSV data export")
    print("-" * 70)
    
    # Get location from user
    location = input("\n📍 Enter location (city name or lat,lon): ").strip()
    
    if not location:
        location = "New Delhi"
        print(f"   Using default location: {location}")
    
    try:
        # PART 1: Fetch and display current weather
        print("\n" + "=" * 50)
        print("PART 1: REAL-TIME WEATHER DATA")
        print("=" * 50)
        
        current_weather = fetch_current_weather(location)
        display_current_weather(current_weather)
        
        # PART 2: Fetch and process historical data
        print("\n" + "=" * 50)
        print("PART 2: 30-DAY HISTORICAL DATA")
        print("=" * 50)
        
        historical_data = fetch_historical_data(
            current_weather['latitude'],
            current_weather['longitude'],
            days=30
        )
        
        # Process daily changes and assign colors
        processed_data = process_daily_changes(historical_data)
        
        # PART 3: Generate visualizations
        print("\n" + "=" * 50)
        print("PART 3: GENERATING VISUALIZATIONS")
        print("=" * 50)
        
        location_name = current_weather['location']
        
        # Generate all three graphs
        temp_graph = create_temperature_graph(processed_data, location_name)
        precip_graph = create_precipitation_graph(processed_data, location_name)
        wind_graph = create_wind_pressure_graph(processed_data, location_name)
        
        # Export data to CSV
        csv_file = export_to_csv(processed_data, location_name)
        
        # Summary
        print("\n" + "=" * 70)
        print("✅ ALL TASKS COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\n📊 OUTPUT FILES GENERATED:")
        print(f"   1. {temp_graph}")
        print(f"   2. {precip_graph}")
        print(f"   3. {wind_graph}")
        print(f"   4. {csv_file}")
        print("\n📁 All files saved in:", os.path.abspath(OUTPUT_DIR))
        print("=" * 70)
        
        # Ask if user wants to display graphs
        show_graphs = input("\n🖼️  Would you like to display the graphs? (y/n): ").strip().lower()
        if show_graphs == 'y':
            print("\nOpening graphs in viewer...")
            # Re-create and show graphs interactively
            import webbrowser
            webbrowser.open(os.path.abspath(temp_graph))
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nPlease check:")
        print("  1. Your internet connection")
        print("  2. API key configuration (if using live data)")
        print("  3. Location spelling")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    sys.exit(main())
