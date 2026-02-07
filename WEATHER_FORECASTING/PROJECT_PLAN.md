# Weather Forecast Web Application with ML Models - Project Plan

## 1. Executive Summary

This project aims to build a comprehensive, educational weather forecasting web application using Python and Streamlit. The application will serve dual purposes: providing accurate weather forecasts and educating users about the underlying machine learning models used in meteorology.

The core value proposition lies in its transparency. Unlike standard weather apps that give a single number, this application will show predictions from multiple models (Prophet, XGBoost, LSTM), explain how each model arrived at its conclusion, and compare their performance. This transparency transforms a simple utility into an interactive learning tool for aspiring data scientists and curious users.

Our technology stack leverages **Streamlit** for rapid UI development, **Meteostat** for historical data acquisition, and **OpenWeatherMap** for real-time data integration. The project is designed to be completed in 6 weeks, resulting in a deployable portfolio piece hosted on Streamlit Cloud.

---

## 2. Model Selection & Strategy

To balance educational value with implementation feasibility and performance, we have selected the following three models. Each represents a distinct approach to time-series forecasting.

### Selected Models

| Model | Type | Why Selected | Difficulty | Computational Load |
| :--- | :--- | :--- | :--- | :--- |
| **Prophet** (by Meta) | Additive Regression | Industry standard for business time-series; handles seasonality and holidays exceptionally well out-of-the-box. | Beginner | Low |
| **XGBoost** | Gradient Boosting | Represents the state-of-the-art in tabular ML; excellent for capturing non-linear relationships and feature interactions. | Intermediate | Low-Medium |
| **LSTM** (Long Short-Term Memory) | Deep Learning (RNN) | The "Gold Standard" for sequential deep learning; demonstrates understanding of neural networks and temporal dependencies. | Advanced | High (Training) / Low (Inference) |

### Implementation Strategy

1.  **Prophet**:
    *   **Input**: Date (`ds`) and Target (`y` - e.g., Temperature).
    *   **Configuration**: Enable daily seasonality.
    *   **Educational Angle**: Explain trend decomposition (Trend + Seasonality + Noise).
2.  **XGBoost**:
    *   **Input**: Lagged features (Temp t-1, Temp t-2), Rolling means, Month, Day of Year.
    *   **Educational Angle**: Feature importance visualization (which variables matter most?).
3.  **LSTM**:
    *   **Input**: Sequence of past 30 days data (3D tensor: Samples, Time Steps, Features).
    *   **Architecture**: Simple 1-2 layer LSTM + Dense output layer.
    *   **Educational Angle**: Visualizing how the network "remembers" past states.

---

## 3. Technical Architecture

### A. Technology Stack

*   **Core Framework**: Streamlit (Python 3.9+)
*   **Data Processing**: Pandas, NumPy
*   **Machine Learning**:
    *   `prophet`
    *   `xgboost`
    *   `tensorflow` (Keras) or `pytorch` (for LSTM)
    *   `scikit-learn` (Metrics, Preprocessing)
*   **Data Source APIs**:
    *   **Historical**: `meteostat` (Python library, free, no API key needed usually).
    *   **Real-time/Forecast**: OpenWeatherMap API (Free Tier).
*   **Visualization**: Plotly (Interactive charts), Matplotlib/Seaborn (Static analysis).

### B. Project Structure

```
weather-forecast-app/
├── .streamlit/
│   └── config.toml          # Theme and server settings
├── app.py                   # Main entry point
├── config.py                # Global configurations (API keys, constants)
├── requirements.txt         # Dependencies
├── Dockerfile               # Deployment containerization (optional)
├── data/
│   ├── raw/                 # Downloaded historical CSVs
│   └── processed/           # Cleaned/Feature-engineered data
├── models/
│   ├── saved/               # Serialized model files (.json, .h5, .pkl)
│   ├── prophet_model.py     # Prophet implementation class
│   ├── xgboost_model.py     # XGBoost implementation class
│   └──- lstm_model.py       # LSTM implementation class
├── pages/
│   ├── 1_Dashboard.py
│   ├── 2_Real_Time_Weather.py
│   ├── 3_Forecast_Comparisons.py
│   ├── 4_Model_Lab.py       # Educational sandbox
│   └── 5_Settings.py
├── utils/
│   ├── data_loader.py       # Meteostat/OpenWeatherMap integration
│   ├── preprocessing.py     # Data cleaning pipelines
│   └── visualization.py     # Chart generation functions
└── assets/
    ├── images/              # Icons, diagrams
    └── css/                 # Custom CSS for styling
```

---

## 4. Data Pipeline Architecture

1.  **Data Collection (Offline/Training)**:
    *   User selects a city.
    *   `meteostat` fetches daily weather data for the last 5-10 years.
    *   Data is cached locally in `data/raw/` to prevent re-fetching.
2.  **Preprocessing**:
    *   Handle missing values (interpolation).
    *   **Feature Engineering**: Create lag features (t-1, t-7), rolling averages (7-day, 30-day), and cyclical date features (Sin/Cos of Day/Month).
    *   **Normalization**: MinMax scaling for LSTM.
3.  **Model Training**:
    *   Triggered manually or on first run for a new city.
    *   Models are trained on the processed history.
    *   Models are saved to `models/saved/`.
4.  **Inference (Real-time)**:
    *   App loads the saved models.
    *   App fetches *current* weather + last 30 days history from OpenWeatherMap/Meteostat to construct the input vector.
    *   Models generate predictions for the next 7 days.
5.  **Visualization**:
    *   Predictions are aggregated into a common DataFrame and passed to Plotly for rendering.

---

## 5. User Interface & Experience (UX)

### Design Philosophy
*   **Aesthetic**: "Glassmorphism" or clean Dark Mode using Streamlit's theming. Deep blues and purples.
*   **Typography**: Sans-serif (Source Sans Pro or Roboto) for readability.

### Page Flow
1.  **Dashboard (Home)**:
    *   **Hero Section**: Current temperature and condition (big, bold).
    *   **City Search**: Prominent search bar.
    *   **Quick Metrics**: Humidity, Wind, Pressure cards.
2.  **Comparison Forecast**:
    *   **Main Chart**: Multi-line chart showing:
        *   Line 1: Model A Prediction
        *   Line 2: Model B Prediction
        *   Line 3: Model C Prediction
        *   Dotted Line: Historical Average (Baseline)
    *   **Confidence Intervals**: Shaded regions around Prophet predictions.
3.  **Model Lab (Education)**:
    *   **Tabs**: One for each model.
    *   **Content**: "How it works" text + Diagram.
    *   **Interactive**: Sliders to change input parameters (e.g., "Increase humidity by 10% - how does the prediction change?").

---

## 6. Implementation Roadmap

### Phase 1: Foundation (Week 1)
*   [x] Setup Git repository and Python environment.
*   [ ] Implement `Meteostat` data loader.
*   [ ] Create basic Streamlit dashboard framework.
*   [ ] Build "Settings" page for City selection.

### Phase 2: Baseline & Prophet (Week 2)
*   [ ] Implement basic data preprocessing.
*   [ ] Train and integrate the **Prophet** model.
*   [ ] Create visualizations for Prophet components (trend vs seasonality).

### Phase 3: Advanced Models (Weeks 3-4)
*   [ ] Implement **XGBoost** with sliding window feature engineering.
*   [ ] Implement **LSTM** using TensorFlow/Keras.
*   [ ] Add model caching and serialization (saving/loading models).

### Phase 4: Integration & Forecasts (Week 5)
*   [ ] Connect OpenWeatherMap API for real-time consistency checks.
*   [ ] Build the "7-Day Forecast" comparison page.
*   [ ] Implement the "Model Lab" educational content.

### Phase 5: Polish & Deploy (Week 6)
*   [ ] Refine UI (custom CSS, meaningful tooltips).
*   [ ] Write unit tests for data pipeline.
*   [ ] Deploy to Streamlit Cloud.
*   [ ] Final documentation (README).

---

## 7. Resource Requirements

### Python Packages (requirements.txt)
```text
streamlit
pandas
numpy
plotly
meteostat
prophet
xgboost
tensorflow  # or pytorch
scikit-learn
requests
joblib
pyyaml
```

### APIs
1.  **OpenWeatherMap**: Sign up for "Current Weather Data" (Free Tier: 60 calls/minute).
2.  **Meteostat**: No API key required for basic Python library usage.

### Computational Resources
*   **Development**: Standard Laptop (8GB+ RAM recommended for training models).
*   **Deployment**: Streamlit Cloud (Free tier provides decent CPU/RAM, but LSTM training might be slow; consider training locally and uploading saved models).

---

## 8. Development Guidelines

*   **Docstrings**: Every function must have numpy-style docstrings suitable for educational reading.
*   **Type Hinting**: Use Python type hints (`def train(df: pd.DataFrame) -> Model:`) for clarity.
*   **Modular Code**: Do not write monolithic scripts. Use the `utils/` folder for helper functions.
*   **Caching**: Aggressively use `@st.cache_data` and `@st.cache_resource` to keep the app snappy.
