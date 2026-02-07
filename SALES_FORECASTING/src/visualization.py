"""
Visualization Module
Interactive Plotly charts for sales forecasting.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MODEL_COLORS, DATE_COLUMN, QUANTITY_COLUMN


def plot_historical_data(
    data: pd.DataFrame,
    date_col: str = DATE_COLUMN,
    value_col: str = QUANTITY_COLUMN,
    title: str = "Historical Sales Data"
) -> go.Figure:
    """
    Create an interactive line chart of historical data.
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data[date_col],
        y=data[value_col],
        mode='lines',
        name='Historical',
        line=dict(color=MODEL_COLORS['Historical'], width=2)
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=20)),
        xaxis_title="Date",
        yaxis_title="Quantity",
        hovermode='x unified',
        template='plotly_white',
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def plot_forecast_comparison(
    historical_data: pd.DataFrame,
    forecasts: Dict[str, pd.DataFrame],
    date_col: str = DATE_COLUMN,
    value_col: str = QUANTITY_COLUMN,
    title: str = "Forecast Comparison"
) -> go.Figure:
    """
    Create comparison chart with historical data and multiple model forecasts.
    """
    fig = go.Figure()
    
    # Historical data
    fig.add_trace(go.Scatter(
        x=historical_data[date_col],
        y=historical_data[value_col],
        mode='lines',
        name='Historical',
        line=dict(color=MODEL_COLORS['Historical'], width=2)
    ))
    
    # Add each forecast
    for model_name, forecast_df in forecasts.items():
        color = MODEL_COLORS.get(model_name, '#888888')
        
        # Main forecast line
        fig.add_trace(go.Scatter(
            x=forecast_df['Date'],
            y=forecast_df['Forecast'],
            mode='lines',
            name=model_name,
            line=dict(color=color, width=2, dash='dash')
        ))
        
        # Add confidence interval if available
        if 'Lower_CI' in forecast_df.columns and 'Upper_CI' in forecast_df.columns:
            fig.add_trace(go.Scatter(
                x=pd.concat([forecast_df['Date'], forecast_df['Date'][::-1]]),
                y=pd.concat([forecast_df['Upper_CI'], forecast_df['Lower_CI'][::-1]]),
                fill='toself',
                fillcolor=color.replace(')', ', 0.1)').replace('rgb', 'rgba'),
                line=dict(color='rgba(0,0,0,0)'),
                name=f'{model_name} CI',
                showlegend=False,
                hoverinfo='skip'
            ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=20)),
        xaxis_title="Date",
        yaxis_title="Quantity",
        hovermode='x unified',
        template='plotly_white',
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def plot_metrics_comparison(
    metrics_df: pd.DataFrame,
    title: str = "Model Performance Comparison"
) -> go.Figure:
    """
    Create bar chart comparing model metrics.
    """
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=('MAE (Lower is Better)', 'RMSE (Lower is Better)', 'MAPE % (Lower is Better)')
    )
    
    colors = [MODEL_COLORS.get(m, '#888888') for m in metrics_df['Model']]
    
    # MAE
    fig.add_trace(
        go.Bar(x=metrics_df['Model'], y=metrics_df['MAE'], marker_color=colors, name='MAE'),
        row=1, col=1
    )
    
    # RMSE
    fig.add_trace(
        go.Bar(x=metrics_df['Model'], y=metrics_df['RMSE'], marker_color=colors, name='RMSE'),
        row=1, col=2
    )
    
    # MAPE
    fig.add_trace(
        go.Bar(x=metrics_df['Model'], y=metrics_df['MAPE'], marker_color=colors, name='MAPE'),
        row=1, col=3
    )
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=20)),
        showlegend=False,
        template='plotly_white',
        height=350
    )
    
    return fig


def plot_single_forecast(
    historical_data: pd.DataFrame,
    forecast_df: pd.DataFrame,
    model_name: str,
    date_col: str = DATE_COLUMN,
    value_col: str = QUANTITY_COLUMN
) -> go.Figure:
    """
    Create chart for single model forecast with confidence intervals.
    """
    fig = go.Figure()
    
    color = MODEL_COLORS.get(model_name, '#888888')
    
    # Historical
    fig.add_trace(go.Scatter(
        x=historical_data[date_col],
        y=historical_data[value_col],
        mode='lines',
        name='Historical',
        line=dict(color=MODEL_COLORS['Historical'], width=2)
    ))
    
    # Confidence interval
    if 'Lower_CI' in forecast_df.columns:
        fig.add_trace(go.Scatter(
            x=pd.concat([forecast_df['Date'], forecast_df['Date'][::-1]]),
            y=pd.concat([forecast_df['Upper_CI'], forecast_df['Lower_CI'][::-1]]),
            fill='toself',
            fillcolor=f'rgba(100, 100, 100, 0.2)',
            line=dict(color='rgba(0,0,0,0)'),
            name='95% Confidence',
            hoverinfo='skip'
        ))
    
    # Forecast
    fig.add_trace(go.Scatter(
        x=forecast_df['Date'],
        y=forecast_df['Forecast'],
        mode='lines+markers',
        name=f'{model_name} Forecast',
        line=dict(color=color, width=3)
    ))
    
    fig.update_layout(
        title=dict(text=f'{model_name} Forecast', font=dict(size=20)),
        xaxis_title="Date",
        yaxis_title="Quantity",
        hovermode='x unified',
        template='plotly_white',
        height=450,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig
