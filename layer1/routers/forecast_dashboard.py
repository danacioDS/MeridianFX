"""
Forecast Dashboard Router — Análisis completo de tendencia y forecast.
"""

from fastapi import APIRouter, Path, Query
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from layer2.data.provider import DataProvider
from layer2.features.technical import TechnicalFeatures
from layer2.engine import DecisionEngine
from layer2.data.macro.service import MacroService

router = APIRouter(prefix="/v1/fx", tags=["forecast-dashboard"])

data_provider = DataProvider()
engine = DecisionEngine()
macro_service = MacroService()

def calculate_trend(df: pd.DataFrame, days: int) -> dict:
    """Calcula tendencia para un período específico."""
    if len(df) < days:
        return {"return": 0.0, "direction": "NEUTRAL", "strength": 0.0}
    
    start_price = df['Close'].iloc[-days]
    end_price = df['Close'].iloc[-1]
    returns = ((end_price - start_price) / start_price) * 100
    
    direction = "UP" if returns > 0 else "DOWN" if returns < 0 else "NEUTRAL"
    strength = min(abs(returns) / 10, 1.0)
    
    return {
        "return": round(returns, 2),
        "direction": direction,
        "strength": round(strength, 3)
    }

def calculate_volatility(df: pd.DataFrame, days: int = 30) -> float:
    """Calcula volatilidad anualizada."""
    if len(df) < days:
        return 0.0
    
    returns = df['Close'].pct_change().dropna().tail(days)
    if len(returns) < 2:
        return 0.0
    
    daily_vol = returns.std()
    annual_vol = daily_vol * np.sqrt(252)
    return round(annual_vol * 100, 2)

def calculate_forecast(pair: str, df: pd.DataFrame, horizon_days: int = 30) -> dict:
    """Calcula forecast usando XGBoost."""
    try:
        df_feat = TechnicalFeatures.generate(df)
        feature_cols = TechnicalFeatures.get_feature_names()
        
        # Usar últimas features para predicción
        latest_features = df_feat[feature_cols].iloc[-1:].dropna()
        
        if latest_features.empty or not engine.xgb_model or not engine.xgb_model.model:
            return {"direction": "UNKNOWN", "probability": 0.5, "expected_return": 0.0}
        
        pred = engine.xgb_model.predict(latest_features)
        probability = pred.get('probability', 0.5)
        
        # Estimar retorno esperado
        current_price = df['Close'].iloc[-1]
        expected_return = (probability - 0.5) * 0.05 * (horizon_days / 30)
        
        # Determinar direction basado en expected_return (consistente)
        if expected_return > 0.001:
            direction = "UP"
        elif expected_return < -0.001:
            direction = "DOWN"
        else:
            direction = "NEUTRAL"
        
        # Intervalo de confianza
        volatility = calculate_volatility(df, 30)
        ci_95_lower = current_price * (1 - 0.02 * (horizon_days / 30) * (volatility / 20))
        ci_95_upper = current_price * (1 + 0.02 * (horizon_days / 30) * (volatility / 20))
        
        return {
            "direction": direction,
            "probability": round(probability, 4),
            "expected_return": round(expected_return * 100, 2),
            "current_price": round(current_price, 4),
            "volatility": volatility,
            "ci_95_lower": round(ci_95_lower, 4),
            "ci_95_upper": round(ci_95_upper, 4)
        }
    except Exception as e:
        return {"direction": "UNKNOWN", "probability": 0.5, "expected_return": 0.0}

@router.get("/{pair:path}/forecast-dashboard")
async def get_forecast_dashboard(
    pair: str = Path(..., description="Currency pair, e.g. USD/BOB"),
):
    """Obtiene análisis completo de tendencia y forecast."""
    
    # Obtener datos históricos
    result = data_provider.get_historical(pair, period="2y", interval="1d")
    df = result["data"]
    
    if df.empty:
        return {"error": "No data available", "pair": pair}
    
    current_price = float(df['Close'].iloc[-1])
    previous_price = float(df['Close'].iloc[-2]) if len(df) > 1 else current_price
    
    # Cambio diario
    change_abs = current_price - previous_price
    change_pct = (change_abs / previous_price) * 100 if previous_price != 0 else 0
    
    # Tendencias por período
    trends = {
        "1m": calculate_trend(df, 20),
        "3m": calculate_trend(df, 60),
        "6m": calculate_trend(df, 120),
        "1y": calculate_trend(df, 252)
    }
    
    # Volatilidad
    volatility = calculate_volatility(df, 30)
    
    # Forecasts por horizonte
    forecasts = {
        "30d": calculate_forecast(pair, df, 30),
        "60d": calculate_forecast(pair, df, 60),
        "90d": calculate_forecast(pair, df, 90)
    }
    
    # Histórico para gráfico
    history = []
    for idx, row in df.iterrows():
        history.append({
            "date": idx.strftime("%Y-%m-%d"),
            "close": float(row['Close']),
            "open": float(row['Open']),
            "high": float(row['High']),
            "low": float(row['Low'])
        })
    
    # Contexto macro
    try:
        import asyncio
        macro_context = asyncio.run(macro_service.get_macro_context())
        macro_summary = macro_context.get("summary", {})
        macro_indicators = macro_context.get("indicators", {})
    except Exception:
        macro_summary = {}
        macro_indicators = {}
    
    return {
        "pair": pair,
        "as_of": datetime.now().isoformat(),
        "spot": {
            "price": round(current_price, 4),
            "previous": round(previous_price, 4),
            "change_abs": round(change_abs, 6),
            "change_pct": round(change_pct, 2)
        },
        "trends": trends,
        "volatility": volatility,
        "forecasts": forecasts,
        "history": history[-365:],  # Último año
        "source": result.get("provider", "yahoo"),
        "freshness": result.get("freshness", "UNKNOWN"),
        "last_date": df.index[-1].strftime("%Y-%m-%d"),
        "macro": {
            "summary": macro_summary,
            "indicators": macro_indicators
        }
    }
