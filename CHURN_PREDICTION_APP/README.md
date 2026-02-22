# 🛡️ ChurnGuard AI — Telecom Customer Churn Prediction

> A production-grade, full-stack ML web application that predicts telecom customer churn using 6 industry-standard models with SHAP explainability.

## 🏗️ Architecture

```
CHURN_PREDICTION_APP/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── api/routes.py      # All REST API endpoints
│   │   ├── config.py          # Configuration & constants
│   │   ├── core/
│   │   │   ├── data_pipeline.py   # Cleaning, encoding, scaling, SMOTE
│   │   │   └── eda.py             # EDA chart computations
│   │   ├── models/
│   │   │   ├── trainer.py     # 6 ML models + Optuna tuning
│   │   │   ├── evaluator.py   # Metrics, confusion matrix, ROC
│   │   │   └── predictor.py   # Single customer prediction
│   │   ├── services/
│   │   │   ├── dataset_service.py # Dataset loading & generation
│   │   │   └── shap_service.py    # SHAP explanations
│   │   └── main.py            # FastAPI entry point
│   ├── data/                  # Auto-generated dataset
│   ├── venv/                  # Python virtual environment
│   └── requirements.txt       # Python dependencies
│
├── frontend/                  # React + Vite frontend
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LandingPage.jsx    # Upload / load dataset
│   │   │   ├── CleaningPage.jsx   # Data cleaning report
│   │   │   ├── EDAPage.jsx        # Interactive charts
│   │   │   ├── TrainingPage.jsx   # Model training & evaluation
│   │   │   └── PredictPage.jsx    # Single customer prediction
│   │   ├── services/api.js    # Axios API client
│   │   ├── App.jsx            # Main app with routing
│   │   ├── main.jsx           # Entry point
│   │   └── index.css          # Full design system
│   ├── vite.config.js         # Dev server + API proxy
│   └── package.json           # Node dependencies
│
└── IMPLEMENTATION_PLAN.md     # Detailed technical plan
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm

### 1. Start the Backend

```bash
cd backend

# Create & activate virtual environment (first time only)
python -m venv venv

# Windows
.\venv\Scripts\activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload --port 8000
```

### 2. Start the Frontend

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start dev server (proxies /api to backend)
npm run dev
```

### 3. Open the App

Visit **http://localhost:5173** in your browser.

## 📊 Features

### 1. Dataset Management
- **Default Dataset**: Auto-generated 7,043-row IBM Telco Churn dataset
- **Upload**: Drag & drop any CSV with churn data
- **Preview**: See shape, dtypes, missing values, and first 20 rows

### 2. Data Cleaning Pipeline
- Fix data types (TotalCharges string → numeric)
- Handle missing values (median for numeric, mode for categorical)
- Outlier detection via IQR + Winsorization
- Label encoding for binary features
- One-hot encoding for multi-category features
- StandardScaler for numeric features
- SMOTE for class imbalance (applied only to training set)

### 3. EDA Dashboard (6 Charts)
- Churn distribution (donut chart)
- Churn by Contract Type, Internet Service, Payment Method (grouped bars + churn rate line)
- Tenure vs Churn (histogram)
- Monthly Charges by Churn (box plot statistics)
- Support Calls vs Churn (composite chart)
- Feature Correlation Heatmap (color-coded matrix)

### 4. Model Training & Evaluation
Six models trained and compared:

| Model | Type | Why for Churn |
|-------|------|---------------|
| **Logistic Regression** | Linear baseline | Interpretable, fast, good baseline |
| **Random Forest** | Ensemble (bagging) | Handles non-linear patterns, robust |
| **XGBoost** | Gradient boosting | State-of-the-art, handles imbalance |
| **LightGBM** | Gradient boosting | Fast, memory-efficient, categorical native |
| **CatBoost** | Gradient boosting | Native categorical support, less tuning |
| **Neural Network** | Deep learning | Captures complex interactions |

**Evaluation Metrics**: Accuracy, Precision, Recall ⭐, F1-Score, ROC-AUC
- **Recall** is the key metric for churn (we want to catch all churners)
- Confusion matrices for each model
- Overlaid ROC curves
- SHAP feature importance visualization

**Hyperparameter Tuning**: Optional Optuna Bayesian optimization (20 trials per model)

### 5. Customer Churn Prediction
- Form with all customer features
- Select any trained model
- Color-coded risk gauge (green/yellow/red)
- SHAP explanation showing top reasons driving the prediction

## 🔑 Key Technical Decisions

### Why Recall Matters Most for Churn
Missing a churning customer (False Negative) is far more costly than flagging a loyal customer for a retention offer (False Positive). A missed churner = lost revenue forever. A false positive = a small retention cost.

### Why SMOTE Over Oversampling
SMOTE generates *synthetic* minority samples by interpolating between existing ones, rather than simply duplicating. This gives the model more diverse training examples and reduces overfitting to specific churner profiles.

### Why StandardScaler Over MinMaxScaler
StandardScaler (z-score) preserves the distribution shape with no bounded range, which works better with Logistic Regression and Neural Networks. MinMaxScaler would squash outliers and lose information.

### Why Optuna Over GridSearch
Optuna uses Bayesian optimization (Tree-structured Parzen Estimator) to explore the hyperparameter space *intelligently*, focusing on promising regions. GridSearch exhaustively tries every combination, which is exponentially slower.

## 🌐 Deployment

### Backend (Render)
1. Create a `render.yaml` or add as a Web Service
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel)
1. Connect GitHub repo → select `frontend` directory
2. Build command: `npm run build`
3. Output: `dist`
4. Environment variable: `VITE_API_URL=https://your-backend.onrender.com`

### Environment Variables
| Variable | Where | Purpose |
|----------|-------|---------|
| `VITE_API_URL` | Frontend | Backend API base URL |
| `HOST` | Backend | Bind host (0.0.0.0 for deployment) |
| `PORT` | Backend | Server port |

## 🧪 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/load-default` | Load default dataset |
| POST | `/api/upload` | Upload CSV file |
| GET | `/api/dataset-preview` | Get dataset info |
| POST | `/api/clean` | Run cleaning pipeline |
| GET | `/api/cleaning-report` | Get cleaning report |
| GET | `/api/eda` | Get EDA chart data |
| POST | `/api/train` | Train all 6 models |
| GET | `/api/models` | List available models |
| GET | `/api/evaluation` | Get evaluation results |
| GET | `/api/shap/{model}` | Get SHAP importance |
| POST | `/api/predict` | Predict churn |

## 🎨 Design System
- Dark mode with glassmorphism
- Purple/cyan gradient primary
- Responsive grid layouts
- Framer Motion animations
- Custom risk gauge with conic gradient
- Data tables with hover states
- Color-coded badges for risk levels
