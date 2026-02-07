"""
Sales Forecasting Dashboard
Main Streamlit application for sales forecasting with multiple models.
"""

import streamlit as st
import pandas as pd
import numpy as np
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="Sales Forecasting Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import modules
from config import (
    APP_TITLE, MODEL_COLORS, DATE_COLUMN, QUANTITY_COLUMN, PRODUCT_COLUMN,
    DEFAULT_FORECAST_DAYS, MAX_FORECAST_DAYS, MIN_DATA_POINTS_BASIC, MIN_DATA_POINTS_ADVANCED
)
from src.data_handler import (
    load_data, validate_data, preprocess_data, get_products,
    get_data_summary, generate_sample_data
)
from src.models import (
    SimpleMovingAverage, WeightedMovingAverage,
    ARIMAForecaster, ProphetForecaster, XGBoostForecaster
)
from src.metrics import calculate_all_metrics, format_metrics_table, get_best_model
from src.visualization import (
    plot_historical_data, plot_forecast_comparison,
    plot_metrics_comparison, plot_single_forecast
)


# Custom CSS
def load_css():
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

try:
    load_css()
except:
    pass  # CSS file may not exist yet


# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'forecasts' not in st.session_state:
    st.session_state.forecasts = {}
if 'metrics' not in st.session_state:
    st.session_state.metrics = {}


def display_header():
    """Display app header with title and description."""
    st.title("📊 Sales Forecasting Dashboard")
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 1.5rem; border-radius: 12px; color: white; margin-bottom: 2rem;'>
        <h3 style='margin: 0;'>Welcome to the Sales Forecasting Tool</h3>
        <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>
            Upload your sales data and generate forecasts using 5 different models. 
            Compare results and choose the best model for your business needs.
        </p>
    </div>
    """, unsafe_allow_html=True)


def display_sidebar():
    """Display sidebar with controls."""
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Data source selection
        st.subheader("📁 Data Source")
        data_source = st.radio(
            "Choose data source:",
            ["Upload File", "Use Sample Data"],
            help="Upload your own CSV/Excel file or use generated sample data"
        )
        
        if data_source == "Upload File":
            uploaded_file = st.file_uploader(
                "Upload CSV or Excel file",
                type=['csv', 'xlsx', 'xls'],
                help="File must have columns: Date, Product, Quantity"
            )
            if uploaded_file:
                df, errors = load_data(uploaded_file)
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    is_valid, messages = validate_data(df)
                    for msg in messages:
                        if msg.startswith("✅"):
                            st.success(msg)
                        elif msg.startswith("❌"):
                            st.error(msg)
                        elif msg.startswith("⚠️"):
                            st.warning(msg)
                        else:
                            st.info(msg)
                    
                    if is_valid:
                        st.session_state.data = df
                        st.success("✅ Data loaded successfully!")
        else:
            if st.button("🔄 Generate Sample Data", use_container_width=True):
                with st.spinner("Generating sample data..."):
                    st.session_state.data = generate_sample_data()
                    st.success("✅ Sample data generated!")
        
        st.divider()
        
        # Product selection
        if st.session_state.data is not None:
            st.subheader("📦 Product Selection")
            products = get_products(st.session_state.data)
            selected_product = st.selectbox(
                "Select Product",
                ["All Products"] + products,
                help="Choose a specific product or analyze all products combined"
            )
            st.session_state.selected_product = selected_product
            
            st.divider()
            
            # Forecast configuration
            st.subheader("🔮 Forecast Settings")
            forecast_days = st.slider(
                "Forecast Horizon (days)",
                min_value=7,
                max_value=MAX_FORECAST_DAYS,
                value=DEFAULT_FORECAST_DAYS,
                step=7,
                help="Number of days to forecast into the future"
            )
            st.session_state.forecast_days = forecast_days
            
            st.divider()
            
            # Model selection
            st.subheader("🤖 Model Selection")
            available_models = {
                "Simple Moving Average": True,
                "Weighted Moving Average": True,
                "ARIMA": True,
                "Prophet": True,
                "XGBoost": True
            }
            
            selected_models = []
            for model_name in available_models:
                if st.checkbox(model_name, value=True, key=f"model_{model_name}"):
                    selected_models.append(model_name)
            
            st.session_state.selected_models = selected_models
            
            st.divider()
            
            # Generate forecasts button
            if st.button("🚀 Generate Forecasts", type="primary", use_container_width=True):
                st.session_state.run_forecast = True
            else:
                st.session_state.run_forecast = False
        
        # Footer
        st.divider()
        st.caption("Built with ❤️ using Streamlit")


def run_forecasts(data: pd.DataFrame, product: str, days: int, models: list) -> tuple:
    """Run selected forecasting models and return results."""
    forecasts = {}
    metrics = {}
    
    # Preprocess data for selected product
    processed_data = preprocess_data(data, product)
    
    # Check data sufficiency
    n_points = len(processed_data)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    model_instances = {
        "Simple Moving Average": SimpleMovingAverage(window=7),
        "Weighted Moving Average": WeightedMovingAverage(window=7),
        "ARIMA": ARIMAForecaster(auto_select=True),
        "Prophet": ProphetForecaster(),
        "XGBoost": XGBoostForecaster(n_lags=7)
    }
    
    for i, model_name in enumerate(models):
        status_text.text(f"Running {model_name}...")
        progress_bar.progress((i + 1) / len(models))
        
        try:
            model = model_instances[model_name]
            
            # Check data requirements
            min_required = MIN_DATA_POINTS_ADVANCED if model_name in ["Prophet", "XGBoost"] else MIN_DATA_POINTS_BASIC
            if n_points < min_required:
                st.warning(f"⚠️ {model_name}: Insufficient data (need {min_required} points, have {n_points})")
                continue
            
            # Fit and predict
            model.fit(processed_data, DATE_COLUMN, QUANTITY_COLUMN)
            forecast_df = model.predict(days)
            forecasts[model_name] = forecast_df
            
            # Calculate metrics using fitted values
            fitted = model.get_fitted_values()
            if fitted is not None:
                actual = processed_data[QUANTITY_COLUMN].values
                # Align lengths (fitted may have NaN at start)
                valid_idx = ~np.isnan(fitted)
                if np.sum(valid_idx) > 0:
                    metrics[model_name] = calculate_all_metrics(
                        actual[valid_idx],
                        fitted[valid_idx]
                    )
            
        except Exception as e:
            st.error(f"❌ {model_name} failed: {str(e)}")
    
    progress_bar.empty()
    status_text.empty()
    
    return forecasts, metrics, processed_data


def display_data_overview():
    """Display data overview section."""
    if st.session_state.data is not None:
        st.subheader("📋 Data Overview")
        
        summary = get_data_summary(st.session_state.data)
        
        cols = st.columns(4)
        with cols[0]:
            st.metric("Total Records", f"{summary['total_rows']:,}")
        with cols[1]:
            st.metric("Products", summary['unique_products'])
        with cols[2]:
            st.metric("Date Range", summary['date_range'])
        with cols[3]:
            st.metric("Avg Daily Sales", f"{summary['avg_daily_quantity']:.0f}")
        
        with st.expander("📊 View Data Sample"):
            st.dataframe(st.session_state.data.head(20), use_container_width=True)


def display_results(forecasts: dict, metrics: dict, processed_data: pd.DataFrame):
    """Display forecast results and visualizations."""
    if not forecasts:
        st.warning("No forecasts generated. Please check model requirements.")
        return
    
    st.subheader("📈 Forecast Results")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Comparison View",
        "📉 Individual Models",
        "📏 Model Metrics",
        "📚 Model Guide"
    ])
    
    with tab1:
        st.markdown("### All Models Comparison")
        fig = plot_forecast_comparison(processed_data, forecasts)
        st.plotly_chart(fig, use_container_width=True)
        
        # Best model highlight
        if metrics:
            best = get_best_model(metrics, "RMSE")
            st.success(f"🏆 **Best Performing Model (by RMSE):** {best}")
    
    with tab2:
        st.markdown("### Individual Model Details")
        model_to_view = st.selectbox("Select Model", list(forecasts.keys()))
        
        if model_to_view:
            fig = plot_single_forecast(processed_data, forecasts[model_to_view], model_to_view)
            st.plotly_chart(fig, use_container_width=True)
            
            # Show forecast table
            with st.expander("📋 View Forecast Data"):
                st.dataframe(forecasts[model_to_view], use_container_width=True)
    
    with tab3:
        st.markdown("### Performance Metrics")
        st.markdown("""
        - **MAE** (Mean Absolute Error): Average magnitude of errors
        - **RMSE** (Root Mean Square Error): Penalizes large errors more
        - **MAPE** (Mean Absolute Percentage Error): Percentage error
        """)
        
        if metrics:
            metrics_df = format_metrics_table(metrics)
            
            fig = plot_metrics_comparison(metrics_df)
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(metrics_df.style.highlight_min(axis=0, subset=['MAE', 'RMSE', 'MAPE']),
                        use_container_width=True)
    
    with tab4:
        st.markdown("### Understanding the Models")
        
        model_instances = {
            "Simple Moving Average": SimpleMovingAverage(),
            "Weighted Moving Average": WeightedMovingAverage(),
            "ARIMA": ARIMAForecaster(),
            "Prophet": ProphetForecaster(),
            "XGBoost": XGBoostForecaster()
        }
        
        for model_name in forecasts.keys():
            desc = model_instances[model_name].get_description()
            
            with st.expander(f"📖 {model_name}", expanded=False):
                st.markdown(f"**{desc['brief']}**")
                st.markdown("---")
                
                cols = st.columns(2)
                with cols[0]:
                    st.markdown("**🔧 How it works:**")
                    st.markdown(desc['how_it_works'])
                    
                    st.markdown("**📅 When to use:**")
                    st.markdown(desc['when_to_use'])
                
                with cols[1]:
                    st.markdown("**✅ Strengths:**")
                    st.markdown(desc['strengths'])
                    
                    st.markdown("**⚠️ Limitations:**")
                    st.markdown(desc['limitations'])


def main():
    """Main application entry point."""
    display_header()
    display_sidebar()
    
    # Main content area
    if st.session_state.data is not None:
        display_data_overview()
        
        # Show historical chart
        st.subheader("📈 Historical Data")
        product = getattr(st.session_state, 'selected_product', 'All Products')
        processed = preprocess_data(st.session_state.data, product)
        fig = plot_historical_data(processed, title=f"Historical Sales - {product}")
        st.plotly_chart(fig, use_container_width=True)
        
        # Run forecasts if button was clicked
        if getattr(st.session_state, 'run_forecast', False):
            with st.spinner("🔮 Generating forecasts..."):
                forecasts, metrics, processed_data = run_forecasts(
                    st.session_state.data,
                    st.session_state.selected_product,
                    st.session_state.forecast_days,
                    st.session_state.selected_models
                )
                st.session_state.forecasts = forecasts
                st.session_state.metrics = metrics
                st.session_state.processed_data = processed_data
        
        # Display results if available
        if st.session_state.forecasts:
            display_results(
                st.session_state.forecasts,
                st.session_state.metrics,
                st.session_state.processed_data
            )
    
    else:
        # Welcome screen
        st.info("👆 Please upload data or generate sample data using the sidebar to get started.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            ### 📁 Expected Data Format
            Your data should have these columns:
            - **Date**: Date of sales (e.g., 2025-01-01)
            - **Product**: Product name (e.g., "Laptop Pro")
            - **Quantity**: Number of units sold (e.g., 150)
            """)
        
        with col2:
            st.markdown("""
            ### 🤖 Available Models
            1. **Simple Moving Average** - Basic baseline
            2. **Weighted Moving Average** - Recent-weighted average
            3. **ARIMA** - Statistical time series model
            4. **Prophet** - Facebook's robust forecaster
            5. **XGBoost** - Machine learning approach
            """)


if __name__ == "__main__":
    main()
