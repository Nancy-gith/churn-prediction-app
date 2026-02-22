# 📋 Telecom Customer Churn Prediction — Implementation Plan

## 1. Project Overview

**Goal:** Build a production-grade web app that predicts telecom customer churn using ML models, with an interactive frontend for data exploration, model training, and individual predictions.

**Tech Stack:**
- **Backend:** Python 3.10+, FastAPI, scikit-learn, XGBoost, LightGBM, CatBoost, TensorFlow/Keras
- **Frontend:** React 18, TailwindCSS, Recharts, Framer Motion
- **Data:** IBM Telco Customer Churn dataset (Kaggle)

---

## 2. Project Structure (Final)

```
CHURN_PREDICTION_APP/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app entry point
│   │   ├── config.py                # App configuration
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py            # All API endpoints
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── data_pipeline.py     # Data cleaning & preprocessing
│   │   │   ├── eda.py               # EDA computations
│   │   │   ├── feature_engineering.py  # Feature encoding, scaling
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── trainer.py           # Model training orchestrator
│   │   │   ├── evaluator.py         # Metrics, ROC, confusion matrix
│   │   │   ├── predictor.py         # Single customer prediction
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── dataset_service.py   # Dataset loading, Kaggle fetch
│   │   │   ├── shap_service.py      # SHAP explanations
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── helpers.py           # Utility functions
│   ├── data/                        # Stored datasets
│   │   └── telco_churn.csv          # Default dataset
│   ├── saved_models/                # Persisted trained models
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/              # Reusable UI components
│   │   ├── pages/                   # Page-level components
│   │   ├── services/                # API client
│   │   ├── hooks/                   # Custom React hooks
│   │   ├── utils/                   # Frontend utilities
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
└── IMPLEMENTATION_PLAN.md
```

---

## 3. Data Pipeline — Decisions & Rationale

### 3.1 Missing Values Strategy
| Column           | Type        | Strategy                                           |
|------------------|-------------|------------------------------------------------------|
| TotalCharges     | Numeric     | Convert to float, fill NaN with median (robust to outliers) |
| SupportCalls     | Numeric     | Fill with 0 (no call = 0 calls)                     |
| Categoricals     | Categorical | Fill with mode (most common value)                   |
| CustomerID/Name  | Identifier  | Drop — not predictive features                       |
| PhoneNumber/SIM  | Identifier  | Drop — not predictive features                       |

**Why median for numerics?** Mean is sensitive to outliers. For `TotalCharges`, long-tenured customers skew the distribution. Median preserves the central tendency.

### 3.2 Data Type Fixes
- `TotalCharges` often arrives as a string (whitespace for new customers). Convert to float, coerce errors to NaN, then impute.
- `SeniorCitizen` may arrive as 0/1 int — keep as-is for binary encoding.

### 3.3 Outlier Detection
- Use IQR method (Q1 - 1.5*IQR, Q3 + 1.5*IQR) for `MonthlyCharges`, `TotalCharges`, `Tenure`.
- **Treatment:** Cap at boundaries (Winsorization) rather than removing — we don't want to lose data in an already imbalanced dataset.

### 3.4 Encoding Strategy
| Feature Type      | Encoding           | Why                                                      |
|-------------------|--------------------|-----------------------------------------------------------|
| Binary (Yes/No)   | Label Encoding     | Only 2 categories, ordinal encoding is sufficient         |
| Nominal (3+ cats) | One-Hot Encoding   | No ordinal relationship; one-hot preserves independence   |
| Target (Churn)    | Binary (0/1)       | Standard for classification                              |

**Why not Target Encoding?** Risk of data leakage if not done carefully with cross-validation folds.

### 3.5 Feature Scaling
- **StandardScaler** for Logistic Regression and Neural Network (algorithms sensitive to feature magnitude).
- Tree-based models (RF, XGBoost, LightGBM, CatBoost) do NOT need scaling — they split on feature values, not magnitudes.

### 3.6 Class Imbalance Handling
- **SMOTE (Synthetic Minority Over-sampling Technique)** on training data only.
- **Why SMOTE over random oversampling?** Random oversampling duplicates exact rows → overfitting. SMOTE creates synthetic interpolations → better generalization.
- **Why not undersampling?** Telco datasets are already not huge (~7K rows). Removing majority class data loses valuable info.
- **Critical:** Apply SMOTE AFTER train-test split. Never SMOTE the test set.

---

## 4. ML Models — Why Each One

### 4.1 Logistic Regression (Baseline)
- **Why:** Industry standard baseline. Interpretable coefficients tell you exactly how each feature affects churn probability.
- **How it works:** Fits a linear boundary in feature space, outputs probabilities via sigmoid function.
- **In churn context:** "For every $10 increase in monthly charges, churn probability increases by X%."

### 4.2 Random Forest
- **Why:** Handles non-linear relationships, resistant to overfitting via bagging.
- **How it works:** Ensemble of decision trees, each trained on a random subset of features and data. Final prediction = majority vote.
- **In churn context:** Captures complex interactions (e.g., high charges + month-to-month contract = high churn risk).

### 4.3 XGBoost
- **Why:** Gold standard for structured/tabular data competitions. Sequential boosting corrects previous trees' errors.
- **How it works:** Gradient boosting — each new tree focuses on the residual errors of the ensemble so far.
- **In churn context:** Excellent at finding the small signals that differentiate churners from non-churners.

### 4.4 LightGBM
- **Why:** Faster than XGBoost for large datasets, uses histogram-based splits.
- **How it works:** Similar to XGBoost but grows trees leaf-wise instead of level-wise → deeper, more accurate trees.
- **In churn context:** Production-ready — handles categoricals natively, fast inference.

### 4.5 CatBoost
- **Why:** Best native handling of categorical features. No need for manual encoding.
- **How it works:** Uses ordered boosting + symmetric trees. Prevents target leakage during training.
- **In churn context:** Contract type, payment method, internet service are all categoricals — CatBoost handles them optimally.

### 4.6 Neural Network (Keras)
- **Why:** Can learn arbitrarily complex patterns. Industry interest in deep learning for tabular data.
- **How it works:** Multi-layer perceptron with ReLU activations and sigmoid output. Dropout for regularization.
- **In churn context:** Captures non-linear feature interactions that linear models miss, but may overfit on small datasets.

---

## 5. Evaluation Metrics — What Matters for Churn

### The Critical Metric: **Recall (Sensitivity)**
- **Why?** In churn prediction, the cost of missing a churner (false negative) is FAR higher than the cost of a false alarm (false positive).
- If you predict "won't churn" for someone who DOES churn → you lose that customer forever.
- If you predict "will churn" for someone who doesn't → you just send them a retention offer (minor cost).

### Full Metrics Suite:
| Metric     | What it measures                                    |
|------------|------------------------------------------------------|
| Accuracy   | Overall correctness — misleading with imbalanced data |
| Precision  | Of predicted churners, how many actually churned?     |
| Recall     | Of actual churners, how many did we catch?            |
| F1-Score   | Harmonic mean of precision and recall                 |
| ROC-AUC    | Model's ability to rank churners above non-churners   |

---

## 6. Hyperparameter Tuning — Optuna

**Why Optuna over RandomSearchCV?**
1. **Smarter search:** Bayesian optimization (TPE sampler) learns from previous trials
2. **Pruning:** Stops unpromising trials early, saving compute
3. **Flexible:** Can optimize any objective, not just sklearn estimators
4. **Visualization:** Built-in plotting of optimization history

---

## 7. SHAP Explanations

**Why SHAP?**
- Provides individual prediction explanations (not just global feature importance)
- Theoretically grounded in Shapley values from game theory
- Works with ANY model type

---

## 8. Frontend Pages

1. **Landing/Upload** — File upload + default dataset button + preview table
2. **Data Cleaning Report** — Before/after stats, missing values, outlier plots
3. **EDA Dashboard** — 6+ interactive charts
4. **Model Training** — Train all models, compare metrics, ROC curves, SHAP
5. **Predict Churn** — Customer form, model selection, prediction with explanation

---

## 9. Deployment

### Backend → Render (Free Tier)
- Dockerfile or `render.yaml`
- Environment: Python 3.10
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend → Vercel
- Connect GitHub repo
- Build: `npm run build`
- Output: `dist/`

### Connection
- Frontend `.env`: `VITE_API_URL=https://your-backend.onrender.com`
- Backend CORS: Allow Vercel domain

---

## 10. Gotchas & Edge Cases

1. **Data leakage:** Never scale/encode test data using test statistics. Always fit on train, transform on test.
2. **SMOTE on test data:** This is a CRITICAL mistake. SMOTE must only be applied to training data.
3. **TotalCharges whitespace:** IBM dataset has " " (space) in TotalCharges for new customers with 0 tenure. Must handle explicitly.
4. **CatBoost categorical handling:** Pass cat_features indices directly, don't one-hot encode for CatBoost.
5. **SHAP with large models:** Use TreeExplainer for tree models (fast), KernelExplainer for neural net (slow — sample background data).
6. **Neural network on small data:** High risk of overfitting. Use early stopping + dropout.
7. **API timeout on model training:** Training 6 models can take 30-60 seconds. Use async endpoints or SSE for progress.
