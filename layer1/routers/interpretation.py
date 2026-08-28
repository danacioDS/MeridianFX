"""
Interpretation Router — Why Now? con LLM + Fallback + Macro
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import List, Optional, Dict
import logging

from ..decision.decision_context import DecisionEngine
from ..llm.interpreter import EconomicInterpreter
from layer2.data.macro.service import MacroService

router = APIRouter(prefix="/v1/fx", tags=["interpretation"])
logger = logging.getLogger(__name__)

# Inicializar motores
decision_engine = DecisionEngine()
interpreter = EconomicInterpreter()
macro_service = MacroService()


# Datos de forecast alineados con el ranking
FORECAST_DATA = {
    "USD/JPY": {
        "pair": "USD/JPY",
        "direction": "UP",
        "probability": 0.33,
        "expected_return": 0.0002,
        "expected_volatility": 0.12,
        "regime": "RISK_OFF",
        "vix": 16.8,
        "yield_spread": 3.42,
        "policy_divergence": "HIGH",
        "previous_probability": 0.32,
        "previous_edge": 0.07,
        "previous_regime": "RISK_OFF",
    },
    "EUR/USD": {
        "pair": "EUR/USD",
        "direction": "UP",
        "probability": 0.53,
        "expected_return": 0.0016,
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
        "expected_return": -0.0028,
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
        "direction": "DOWN",
        "probability": 0.67,
        "expected_return": -0.0026,
        "expected_volatility": 0.08,
        "regime": "RISK_ON",
        "vix": 16.5,
        "yield_spread": 3.1,
        "policy_divergence": "HIGH",
        "previous_probability": 0.62,
        "previous_edge": 0.75,
        "previous_regime": "RISK_ON",
    },
    "USD/CNY": {
        "pair": "USD/CNY",
        "direction": "DOWN",
        "probability": 0.35,
        "expected_return": -0.0003,
        "expected_volatility": 0.06,
        "regime": "RISK_OFF",
        "vix": 18.0,
        "yield_spread": 2.5,
        "policy_divergence": "MEDIUM",
        "previous_probability": 0.33,
        "previous_edge": 0.10,
        "previous_regime": "RISK_OFF",
    },
    "USD/MXN": {
        "pair": "USD/MXN",
        "direction": "UP",
        "probability": 0.55,
        "expected_return": 0.0017,
        "expected_volatility": 0.14,
        "regime": "RISK_ON",
        "vix": 17.5,
        "yield_spread": 2.2,
        "policy_divergence": "MEDIUM",
        "previous_probability": 0.52,
        "previous_edge": 0.55,
        "previous_regime": "RISK_ON",
    },
    "USD/BRL": {
        "pair": "USD/BRL",
        "direction": "UP",
        "probability": 0.37,
        "expected_return": 0.0005,
        "expected_volatility": 0.18,
        "regime": "RISK_ON",
        "vix": 19.0,
        "yield_spread": 2.0,
        "policy_divergence": "MEDIUM",
        "previous_probability": 0.35,
        "previous_edge": 0.15,
        "previous_regime": "RISK_ON",
    },
    "USD/ARS": {
        "pair": "USD/ARS",
        "direction": "DOWN",
        "probability": 0.65,
        "expected_return": -0.0024,
        "expected_volatility": 0.20,
        "regime": "RISK_OFF",
        "vix": 21.0,
        "yield_spread": 2.6,
        "policy_divergence": "HIGH",
        "previous_probability": 0.60,
        "previous_edge": 0.78,
        "previous_regime": "RISK_OFF",
    },
    "USD/BOB": {
        "pair": "USD/BOB",
        "direction": "DOWN",
        "probability": 0.63,
        "expected_return": -0.0023,
        "expected_volatility": 0.12,
        "regime": "RISK_OFF",
        "vix": 20.5,
        "yield_spread": 2.7,
        "policy_divergence": "HIGH",
        "previous_probability": 0.58,
        "previous_edge": 0.72,
        "previous_regime": "RISK_OFF",
    },
}


def get_forecast_data(pair: str) -> Dict:
    """Obtiene datos de forecast alineados con el ranking."""
    if pair in FORECAST_DATA:
        return FORECAST_DATA[pair]
    
    # Default
    data = FORECAST_DATA["USD/JPY"].copy()
    data["pair"] = pair
    return data


@router.get("/interpretation")
async def get_interpretation(
    pair: str = Query(..., description="Par de divisas, ej: USD/JPY"),
    horizon: str = Query("5D", description="Horizonte de forecast"),
    include_macro: bool = Query(True, description="Incluir contexto macro"),
):
    """
    Obtiene interpretación económica para un par.
    """
    try:
        # 1. Obtener datos reales del forecast
        data = get_forecast_data(pair)
        
        # 2. Obtener contexto macro
        macro_context = None
        if include_macro:
            try:
                macro_context = await macro_service.get_macro_context()
            except Exception as e:
                logger.warning(f"Error fetching macro context: {e}")
        
        # 3. Construir Decision Context
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
            macro_context=macro_context,
        )
        
        # 4. Generar interpretación
        context_dict = context.to_dict()
        bullets = await interpreter.interpret(context_dict)
        
        return {
            "pair": data["pair"],
            "interpretation": bullets,
            "context": context_dict,
            "macro": macro_context,
            "timestamp": datetime.now().isoformat(),
        }
        
    except Exception as e:
        logger.error(f"Error generating interpretation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/macro/status")
async def get_macro_status():
    """Obtiene el estado del servicio macro."""
    return macro_service.get_cache_status()


@router.post("/macro/refresh")
async def refresh_macro():
    """Fuerza la actualización de los datos macro."""
    try:
        macro_context = await macro_service.get_macro_context(force_refresh=True)
        return {
            "status": "refreshed",
            "timestamp": datetime.now().isoformat(),
            "macro": macro_context
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
