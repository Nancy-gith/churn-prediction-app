import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.data_loader import WeatherDataLoader
from utils.preprocessing import WeatherPreprocessor

st.set_page_config(page_title="Weather Dashboard", page_icon="🌤️", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .big-metric {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
    }
    .weather-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;  
        text-align: center;
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
</style>
""", unsafe_allow_html=True)

st.title("🌤️ Live Weather Dashboard - India")
st.markdown("### Real-time weather + 30-day historical analysis")
st.markdown("---")

# Initialize loader
loader = WeatherDataLoader()

# Sidebar for city selection
with st.sidebar:
    st.header("🌍 Select Location")
    
    # Get list of all Indian cities
    city_list = loader.get_city_list()
    
    st.info(f"📍 **{len(city_list)} Indian Cities** available\n\n🌧️ Rain spots | ❄️ Snow destinations")
    
    selected_city = st.selectbox(
        "Choose your city",
        options=city_list,
        index=city_list.index('Mumbai') if 'Mumbai' in city_list else 0,
        help="Select any Indian city to view weather data"
    )
    
    st.markdown("---")
    
    if st.button("🔄 Refresh Data", type="primary", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.markdown("""
    ### 📊 Data Sources
    - **Real-time**: OpenWeatherMap
    - **Historical**: Meteostat
    - **Span**: Last 30 days
    - **Update**: Every 30 min
    
    ### 🌦️ Special Features
    - 🌧️ **Rain destinations**: Cherrapunji, Mawsynram, Mahabaleshwar
    - ❄️ **Snow spots**: Gulmarg, Auli, Leh, Manali
    """)

# Main content
try:
    # Fetch real-time weather
    with st.spinner(f"Fetching live weather for {selected_city}..."):
        realtime = loader.get_realtime_weather(selected_city)
        city_info = WeatherDataLoader.get_city_info(selected_city)
    
    # Display real-time weather in a beautiful card
    st.markdown("## 🌡️ Current Weather")
    
    col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1.5, 1.5, 1.5])
    
    with col1:
        # Main temperature display with icon
        weather_emoji = WeatherDataLoader.get_weather_emoji(realtime['icon'])
        st.markdown(f"""
        <div class="weather-card">
            <h1 style="margin:0; font-size:72px;">{weather_emoji}</h1>
            <h2 style="margin:10px 0;">{selected_city}</h2>
            <p style="margin:5px 0; opacity:0.9;">{city_info['state']}</p>
            <h1 style="margin:15px 0; font-size:64px;">{realtime['temperature']}°C</h1>
            <p style="margin:5px 0; font-size:18px; opacity:0.95;">{realtime['description']}</p>
            <p style="margin:5px 0; opacity:0.8;">Feels like {realtime['feels_like']}°C</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("💧 Humidity", f"{realtime['humidity']}%")
        st.metric("🌫️ Visibility", f"{realtime['visibility']} km")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("💨 Wind Speed", f"{realtime['wind_speed']} km/h")
        st.metric("☁️ Cloud Cover", f"{realtime['clouds']}%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🎚️ Pressure", f"{realtime['pressure']} hPa")
        st.metric("📍 Lat/Lon", f"{city_info['lat']:.2f}°")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col5:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🕐 Updated", realtime['timestamp'].strftime('%H:%M'))
        st.metric("📅 Date", realtime['timestamp'].strftime('%d %b'))
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Fetch historical data (30 days)
    with st.spinner("Loading 30-day historical data..."):
        df = loader.fetch_historical_data(selected_city, days=30)
    
    st.success(f"✅ Loaded {len(df)} days of historical data")
    
    # Calculate 30-day average for comparison
    avg_temp_30days = df['tavg'].mean() if 'tavg' in df.columns else None
    
    # Show comparison between real-time and average
    st.markdown("### 📊 Temperature Comparison: Now vs. 30-Day Average")
    
    comp_col1, comp_col2, comp_col3 = st.columns(3)
    
    with comp_col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%); 
                    padding: 20px; border-radius: 15px; text-align: center;'>
            <h4 style='margin: 0; color: white; opacity: 0.9;'>🔴 NOW (Real-Time)</h4>
            <h1 style='margin: 10px 0; color: white; font-size: 48px;'>{:.1f}°C</h1>
            <p style='margin: 0; color: white; opacity: 0.8;'>Live API data</p>
        </div>
        """.format(realtime['temperature']), unsafe_allow_html=True)
    
    with comp_col2:
        if avg_temp_30days:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #4ECDC4 0%, #6ED9D0 100%); 
                        padding: 20px; border-radius: 15px; text-align: center;'>
                <h4 style='margin: 0; color: white; opacity: 0.9;'>📊 30-DAY AVERAGE</h4>
                <h1 style='margin: 10px 0; color: white; font-size: 48px;'>{:.1f}°C</h1>
                <p style='margin: 0; color: white; opacity: 0.8;'>Historical mean</p>
            </div>
            """.format(avg_temp_30days), unsafe_allow_html=True)
    
    with comp_col3:
        if avg_temp_30days:
            difference = realtime['temperature'] - avg_temp_30days
            is_hotter = difference > 0
            color = '#FF6B6B' if is_hotter else '#4ECDC4'
            arrow = '📈' if is_hotter else '📉'
            comparison = 'HOTTER' if is_hotter else 'COOLER'
            
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, {color} 0%, rgba(255,255,255,0.2) 100%); 
                        padding: 20px; border-radius: 15px; text-align: center; border: 2px solid {color};'>
                <h4 style='margin: 0; opacity: 0.9;'>{arrow} DIFFERENCE</h4>
                <h1 style='margin: 10px 0; font-size: 48px;'>{difference:+.1f}°C</h1>
                <p style='margin: 0; opacity: 0.8; font-weight: bold;'>{comparison} than average</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📈 Temperature Trends", "🌧️ Precipitation", "💨 Wind & Pressure"])
    
    with tab1:
        st.markdown("### Temperature History (Last 30 Days)")
        
        fig = go.Figure()
        
        if 'tavg' in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index, 
                y=df['tavg'],
                name='Average',
                line=dict(color='#FF6B6B', width=3),
                mode='lines+markers'
            ))
        
        if 'tmax' in df.columns and 'tmin' in df.columns:
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
                mode='lines'
            ))
        
        fig.update_layout(
            title=f"Temperature Trends - {selected_city}",
            xaxis_title="Date",
            yaxis_title="Temperature (°C)",
            hovermode='x unified',
            height=450,
            template='plotly_dark',
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Quick stats
        col1, col2, col3, col4 = st.columns(4)
        if 'tavg' in df.columns:
            with col1:
                st.metric("📊 30-Day Average", f"{df['tavg'].mean():.1f}°C")
            with col2:
                st.metric("🔥 Highest", f"{df['tavg'].max():.1f}°C")
            with col3:
                st.metric("❄️ Lowest", f"{df['tavg'].min():.1f}°C")
            with col4:
                st.metric("📏 Range", f"{df['tavg'].max() - df['tavg'].min():.1f}°C")
    
    with tab2:
        st.markdown("### Precipitation & Humidity (Last 30 Days)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'prcp' in df.columns:
                fig_prcp = go.Figure()
                fig_prcp.add_trace(go.Bar(
                    x=df.index,
                    y=df['prcp'],
                    name='Precipitation',
                    marker_color='#4A90E2'
                ))
                fig_prcp.update_layout(
                    title="Daily Precipitation",
                    xaxis_title="Date",
                    yaxis_title="Precipitation (mm)",
                    height=350,
                    template='plotly_dark'
                )
                st.plotly_chart(fig_prcp, use_container_width=True)
                
                total_prcp = df['prcp'].sum()
                rainy_days = (df['prcp'] > 0).sum()
                st.metric("🌧️ Total Rainfall", f"{total_prcp:.1f} mm")
                st.metric("📅 Rainy Days", f"{rainy_days} / {len(df)}")
        
        with col2:
            # Create humidity trend if available (estimated from other metrics)
            st.markdown("#### 💧 Relative Humidity Indicator")
            st.info("Full humidity data requires premium API access. Showing precipitation as proxy.")
            
            if 'prcp' in df.columns:
                # Simple visual indicator
                fig_humidity = px.area(
                    x=df.index,
                    y=df['prcp'].rolling(7).mean(),
                    labels={'x': 'Date', 'y': '7-Day Rolling Avg (mm)'},
                    template='plotly_dark'
                )
                fig_humidity.update_traces(line_color='#9B59B6', fillcolor='rgba(155, 89, 182, 0.3)')
                fig_humidity.update_layout(height=350, title="Moisture Trend (7-day avg)")
                st.plotly_chart(fig_humidity, use_container_width=True)
    
    with tab3:
        st.markdown("### Wind & Atmospheric Pressure (Last 30 Days)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'wspd' in df.columns:
                fig_wind = px.line(
                    x=df.index,
                    y=df['wspd'],
                    labels={'x': 'Date', 'y': 'Wind Speed (km/h)'},
                    template='plotly_dark',
                    title="Wind Speed Variation"
                )
                fig_wind.update_traces(line_color='#2ECC71', line_width=2)
                fig_wind.update_layout(height=350)
                st.plotly_chart(fig_wind, use_container_width=True)
                
                st.metric("💨 Average Wind", f"{df['wspd'].mean():.1f} km/h")
                st.metric("🌪️ Max Gust", f"{df['wspd'].max():.1f} km/h")
        
        with col2:
            if 'pres' in df.columns:
                fig_pres = px.line(
                    x=df.index,
                    y=df['pres'],
                    labels={'x': 'Date', 'y': 'Pressure (hPa)'},
                    template='plotly_dark',
                    title="Atmospheric Pressure"
                )
                fig_pres.update_traces(line_color='#E74C3C', line_width=2)
                fig_pres.update_layout(height=350)
                st.plotly_chart(fig_pres, use_container_width=True)
                
                st.metric("🎚️ Average Pressure", f"{df['pres'].mean():.1f} hPa")
    
    # Store data in session state for other pages
    st.session_state['weather_data'] = df
    st.session_state['selected_city'] = selected_city
    st.session_state['city_info'] = city_info
    st.session_state['realtime_weather'] = realtime
    
    # Footer info
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; opacity: 0.7;'>
        <p>📡 Data updated every 30 minutes | 🗺️ {len(city_list)} Indian cities available</p>
        <p>💾 Historical data cached locally for faster access</p>
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"❌ Error loading weather data: {str(e)}")
    st.info("""
    **Troubleshooting Tips:**
    - Check internet connection
    - Ensure API key is set in `.env` file (optional - mock data will be used otherwise)
    - Try selecting a different city
    """)
