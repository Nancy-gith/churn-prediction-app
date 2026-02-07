import streamlit as st
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Weather Forecast ML Lab",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar
with st.sidebar:
    st.markdown("# 🌤️ Weather ML Lab")
    st.markdown("---")
    st.markdown("""
    ### Navigation Guide
    
    **📊 Dashboard**  
    Load and explore historical weather data
    
    **🔮 Forecast Pages** *(Coming Soon)*  
    - Prophet Model
    - XGBoost Model  
    - LSTM Model
    
    **📚 Model Education** *(Coming Soon)*  
    Learn how each model works
    """)
    
    st.markdown("---")
    st.info("💡 **Tip**: Start with the Dashboard to load data for your city!")

# Main content
st.title("🌤️ Advanced Weather Forecasting Lab")
st.markdown("### *Transparent Machine Learning for Weather Prediction*")
st.markdown("---")

# Introduction
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ## Welcome! 👋
    
    This application is different from typical weather apps. Instead of just showing you a forecast, 
    we **show you how different ML models arrive at their predictions** and let you compare them side-by-side.
    
    ### What Makes This Special?
    
    - **🎓 Educational**: Understand the math and logic behind each forecast model
    - **🔬 Transparent**: See confidence intervals, feature importance, and model internals
    - **⚖️ Comparative**: Compare predictions from multiple industry-standard models
    - **📊 Data-Driven**: Use real historical weather data from global weather stations
    
    ### Three Industry-Standard Models:
    
    1. **📈 Prophet** (by Meta)  
       *Best for*: Detecting seasonal patterns and trend changes  
       *Used by*: Facebook, Uber, Airbnb for business forecasting
    
    2. **🌳 XGBoost**  
       *Best for*: Capturing complex non-linear relationships  
       *Used by*: Kaggle winners, financial institutions
    
    3. **🧠 LSTM (Deep Learning)**  
       *Best for*: Learning long-term temporal dependencies  
       *Used by*: Google, Amazon for sequence prediction
    """)

with col2:
    st.markdown("### 🚀 Quick Start")
    
    st.info("""
    **Step 1**  
    Go to **📊 Dashboard** page
    
    **Step 2**  
    Select your city and load data
    
    **Step 3**  
    Explore visualizations and data quality
    
    **Step 4** *(Coming Soon)*  
    Train models and compare forecasts
    """)
    
    # Status metrics
    st.markdown("### 📊 System Status")
    
    # Check if data is loaded
    data_loaded = 'weather_data' in st.session_state
    city = st.session_state.get('selected_city', 'None')
    
    st.metric("Data Loaded", "Yes" if data_loaded else "No", 
             delta=city if data_loaded else "Load in Dashboard")
    st.metric("Available Cities", "9", delta="Global Coverage")
    st.metric("Data Source", "Meteostat", delta="Free API ✓")

# Features showcase
st.markdown("---")
st.markdown("## 🎯 Key Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 📊 Data Pipeline
    - Historical weather data (1-10 years)
    - Real-time data integration
    - Automatic caching
    - Feature engineering
    - Quality metrics
    """)

with col2:
    st.markdown("""
    ### 🤖 Model Training
    - Prophet (Additive Model)
    - XGBoost (Ensemble)
    - LSTM (Deep Learning)
    - Hyperparameter tuning
    - Cross-validation
    """)

with col3:
    st.markdown("""
    ### 📈 Visualizations
    - Interactive charts (Plotly)
    - Model comparisons
    - Confidence intervals
    - Feature importance
    - Performance metrics
    """)

# Technical details
with st.expander("🔧 Technical Stack"):
    tech_col1, tech_col2 = st.columns(2)
    
    with tech_col1:
        st.markdown("""
        **Frontend & Deployment**
        - Streamlit (Python web framework)
        - Plotly (Interactive visualizations)
        - Streamlit Cloud (Free hosting)
        """)
    
    with tech_col2:
        st.markdown("""
        **Data & ML Libraries**
        - Meteostat (Historical data)
        - Prophet, XGBoost, TensorFlow
        - Scikit-learn, Pandas, NumPy
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Built with ❤️ for data science learning | Free & Open Source</p>
    <p>Data provided by Meteostat | Weather stations worldwide</p>
</div>
""", unsafe_allow_html=True)
