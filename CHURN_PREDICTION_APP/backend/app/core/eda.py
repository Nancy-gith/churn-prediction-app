"""
EDA (Exploratory Data Analysis) computations.

Generates chart-ready JSON data for the frontend.
All computations happen server-side; the frontend only renders.
"""
import pandas as pd
import numpy as np
import math
from typing import Dict, Any, List
from app.config import TARGET_COLUMN


def _sanitize(obj):
    """Recursively replace NaN/Inf with 0 so JSON serialization doesn't blow up."""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return 0
        return obj
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sanitize(v) for v in obj]
    if isinstance(obj, np.floating):
        val = float(obj)
        if math.isnan(val) or math.isinf(val):
            return 0
        return val
    if isinstance(obj, (np.integer,)):
        return int(obj)
    return obj


def compute_churn_distribution(df: pd.DataFrame) -> Dict[str, Any]:
    """Churn distribution for donut/pie chart."""
    counts = df[TARGET_COLUMN].value_counts()
    labels = ["No Churn", "Churn"] if 0 in counts.index else counts.index.tolist()

    return {
        "chart_type": "donut",
        "title": "Churn Distribution",
        "data": [
            {"name": "No Churn", "value": int(counts.get(0, counts.get("No", 0)))},
            {"name": "Churn", "value": int(counts.get(1, counts.get("Yes", 0)))},
        ]
    }


def compute_churn_by_category(df: pd.DataFrame, column: str) -> Dict[str, Any]:
    """Grouped bar chart: churn rate by a categorical column."""
    if column not in df.columns:
        return {"error": f"Column '{column}' not found"}

    target = TARGET_COLUMN
    cross = pd.crosstab(df[column], df[target])

    # Handle both numeric (0/1) and string (Yes/No) target
    if 0 in cross.columns:
        no_col, yes_col = 0, 1
    else:
        no_col, yes_col = "No", "Yes"

    data = []
    for idx in cross.index:
        no_count = int(cross.loc[idx, no_col]) if no_col in cross.columns else 0
        yes_count = int(cross.loc[idx, yes_col]) if yes_col in cross.columns else 0
        total = no_count + yes_count
        data.append({
            "category": str(idx),
            "No Churn": no_count,
            "Churn": yes_count,
            "Churn Rate": round(yes_count / total * 100, 1) if total > 0 else 0,
        })

    return {
        "chart_type": "grouped_bar",
        "title": f"Churn by {column}",
        "data": data
    }


def compute_tenure_vs_churn(df: pd.DataFrame) -> Dict[str, Any]:
    """Histogram of tenure distribution split by churn status."""
    target = TARGET_COLUMN
    bins = list(range(0, 78, 6))  # 6-month bins

    data = []
    for label, group_val in [("No Churn", 0), ("Churn", 1)]:
        if group_val in df[target].values or str(group_val) in df[target].values:
            mask = df[target] == group_val
        else:
            label_map = {"No Churn": "No", "Churn": "Yes"}
            mask = df[target] == label_map[label]

        subset = df.loc[mask, "tenure"] if "tenure" in df.columns else df.loc[mask, "Tenure"]
        hist_values, bin_edges = np.histogram(subset, bins=bins)
        for i, count in enumerate(hist_values):
            bin_label = f"{int(bin_edges[i])}-{int(bin_edges[i+1])}"

            existing = next((d for d in data if d["bin"] == bin_label), None)
            if existing:
                existing[label] = int(count)
            else:
                data.append({"bin": bin_label, label: int(count)})

    return {
        "chart_type": "histogram",
        "title": "Tenure Distribution by Churn Status",
        "data": data
    }


def compute_monthly_charges_boxplot(df: pd.DataFrame) -> Dict[str, Any]:
    """Box plot statistics for MonthlyCharges by churn status."""
    target = TARGET_COLUMN
    col = "MonthlyCharges" if "MonthlyCharges" in df.columns else "monthlycharges"

    data = []
    for label, group_val in [("No Churn", 0), ("Churn", 1)]:
        if group_val in df[target].values:
            mask = df[target] == group_val
        else:
            label_map = {0: "No", 1: "Yes"}
            mask = df[target] == label_map[group_val]

        subset = df.loc[mask, col].dropna()
        q1 = float(subset.quantile(0.25))
        median = float(subset.median())
        q3 = float(subset.quantile(0.75))
        iqr = q3 - q1

        data.append({
            "category": label,
            "min": round(float(max(subset.min(), q1 - 1.5 * iqr)), 2),
            "q1": round(q1, 2),
            "median": round(median, 2),
            "q3": round(q3, 2),
            "max": round(float(min(subset.max(), q3 + 1.5 * iqr)), 2),
            "mean": round(float(subset.mean()), 2),
        })

    return {
        "chart_type": "boxplot",
        "title": "Monthly Charges by Churn Status",
        "data": data
    }


def compute_correlation_heatmap(df: pd.DataFrame) -> Dict[str, Any]:
    """Correlation matrix for all numeric columns."""
    numeric_df = df.select_dtypes(include=[np.number])

    # Limit to top 15 features by correlation with target
    if TARGET_COLUMN in numeric_df.columns:
        correlations = numeric_df.corr()[TARGET_COLUMN].abs().sort_values(ascending=False)
        top_cols = correlations.head(15).index.tolist()
        numeric_df = numeric_df[top_cols]

    corr_matrix = numeric_df.corr().fillna(0).round(3)

    data = []
    columns = corr_matrix.columns.tolist()
    for i, row_name in enumerate(columns):
        for j, col_name in enumerate(columns):
            val = corr_matrix.iloc[i, j]
            val = 0 if (math.isnan(val) or math.isinf(val)) else round(val, 3)
            data.append({
                "x": col_name,
                "y": row_name,
                "value": val
            })

    return {
        "chart_type": "heatmap",
        "title": "Feature Correlation Heatmap",
        "columns": columns,
        "data": data
    }


def compute_support_calls_vs_churn(df: pd.DataFrame) -> Dict[str, Any]:
    """Bar chart of churn rate by number of support calls."""
    col = "SupportCalls" if "SupportCalls" in df.columns else "supportcalls"
    if col not in df.columns:
        # Create synthetic if not present
        return {"chart_type": "bar", "title": "Support Calls vs Churn", "data": []}

    target = TARGET_COLUMN
    grouped = df.groupby(col)[target].agg(["sum", "count"]).reset_index()
    grouped.columns = [col, "churn_count", "total"]
    grouped["churn_rate"] = (grouped["churn_count"] / grouped["total"] * 100).round(1)

    data = []
    for _, row in grouped.iterrows():
        data.append({
            "support_calls": int(row[col]),
            "total_customers": int(row["total"]),
            "churned": int(row["churn_count"]),
            "churn_rate": float(row["churn_rate"]),
        })

    return {
        "chart_type": "bar",
        "title": "Support Calls vs Churn Rate",
        "data": data
    }


def compute_all_eda(df: pd.DataFrame) -> Dict[str, Any]:
    """Run all EDA computations and return combined results."""

    # Determine categorical columns for churn-by-category charts
    category_charts = {}
    for col in ["Contract", "ContractType", "InternetService", "PaymentMethod"]:
        if col in df.columns:
            category_charts[col] = compute_churn_by_category(df, col)

    result = {
        "churn_distribution": compute_churn_distribution(df),
        "churn_by_category": category_charts,
        "tenure_vs_churn": compute_tenure_vs_churn(df),
        "monthly_charges_boxplot": compute_monthly_charges_boxplot(df),
        "correlation_heatmap": compute_correlation_heatmap(df),
        "support_calls_vs_churn": compute_support_calls_vs_churn(df),
        "summary_stats": {
            "total_customers": len(df),
            "churn_rate": round(
                df[TARGET_COLUMN].mean() * 100
                if df[TARGET_COLUMN].dtype in [np.int64, np.float64]
                else (df[TARGET_COLUMN] == "Yes").mean() * 100,
                1
            ),
            "avg_tenure": round(float(
                df["tenure"].mean() if "tenure" in df.columns else
                df["Tenure"].mean() if "Tenure" in df.columns else 0
            ), 1),
            "avg_monthly_charges": round(float(
                df["MonthlyCharges"].mean() if "MonthlyCharges" in df.columns else 0
            ), 2),
        }
    }
    return _sanitize(result)
