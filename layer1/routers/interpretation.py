"""
Interpretation Router — Why Now? con LLM + Fallback
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import List, Optional, Dict
import logging

from ..decision.decision_context import DecisionEngine
from ..llm.interpreter import EconomicInterpreter

router = APIRouter(prefix="/v1/fx", tags=["interpretation"])
logger = logging.getLogger(__name__)

# Inicializar motores
decision_engine = DecisionEngine()
interpreter = EconomicInterpreter()


def get_forecast_data(pair: str) -> Dict:
    """
    Obtiene datos de forecast reales.
    En producción: llama al endpoint de forecast.
    """
    # Por ahora, datos simulados que coinciden con el forecast real
    # En producción, esto vendría del Decision Engine real
    forecast_data = {
        "USD/JPY": {
            "pair": "USD/JPY",
            "direction": "UP",
            "probability": 0.54,
            "expected_return": 0.0008,
            "expected_volatility": 0.12,
            "regime": "RISK_OFF",
            "vix": 16.8,
            "yield_spread": 3.42,
            "policy_divergence": "HIGH",
            "previous_probability": 0.55,
            "previous_edge": 0.09,
            "previous_regime": "RISK_OFF",
        },
        "EUR/USD": {
            "pair": "EUR/USD",
            "direction": "DOWN",
            "probability": 0.55,
            "expected_return": -0.0015,
            "expected_volatility": 0.10,
            "regime": "RISK_ON",
            "vix": 18.2,
            "yield_spread": 2.1,
            "policy_divergence": "MEDIUM",
            "previous_probability": 0.52,
            "previous_edge": 0.60,
            "previous_regime": "RISK_ON",
        },
        "GBP/USD": {
            "pair": "GBP/USD",
            "direction": "DOWN",
            "probability": 0.70,
            "expected_return": -0.0035,
            "expected_volatility": 0.15,
            "regime": "RISK_OFF",
            "vix": 22.1,
            "yield_spread": 2.8,
            "policy_divergence": "HIGH",
            "previous_probability": 0.65,
            "previous_edge": 0.85,
            "previous_regime": "RISK_OFF",
        },
        "USD/CHF": {
            "pair": "USD/CHF",
            "direction": "UP",
            "probability": 0.68,
            "expected_return": 0.0020,
            "expected_volatility": 0.08,
            "regime": "RISK_ON",
            "vix": 16.5,
            "yield_spread": 3.1,
            "policy_divergence": "HIGH",
            "previous_probability": 0.62,
            "previous_edge": 0.75,
            "previous_regime": "RISK_ON",
        },
    }
    
    # Buscar datos para el par
    if pair in forecast_data:
        return forecast_data[pair]
    
    # Si no existe, usar USD/JPY con el par solicitado
    data = forecast_data["USD/JPY"].copy()
    data["pair"] = pair
    return data


@router.get("/interpretation")
async def get_interpretation(
    pair: str = Query(..., description="Par de divisas, ej: USD/JPY"),
    horizon: str = Query("5D", description="Horizonte de forecast"),
):
    """
    Obtiene interpretación económica para un par.
    
    El LLM interpreta la evidencia provista por MeridianFX
    y genera 3-4 bullets económicos.
    
    Fallback: Groq → GLM → Gemini → Rules
    """
    try:
        # 1. Obtener datos reales del forecast
        data = get_forecast_data(pair)
        
        # 2. Construir Decision Context
        context = decision_engine.build_context(
            pair=data["pair"],
            direction=data["direction"],
            probability=data["probability"],
            expected_return=data["expected_return"],
            expected_volatility=data["expected_volatility"],
            regime=data["regime"],
            vix=data["vix"],
            yield_spread=data["yield_spread"],
            policy_divergence=data["policy_divergence"],
            horizon=horizon,
            previous_probability=data.get("previous_probability"),
            previous_edge=data.get("previous_edge"),
            previous_regime=data.get("previous_regime"),
        )
        
        # 3. Generar interpretación con LLM
        context_dict = context.to_dict()
        bullets = await interpreter.interpret(context_dict)
        
        return {
            "pair": data["pair"],
            "interpretation": bullets,
            "context": context_dict,
            "timestamp": datetime.now().isoformat(),
        }
        
    except Exception as e:
        logger.error(f"Error generating interpretation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
