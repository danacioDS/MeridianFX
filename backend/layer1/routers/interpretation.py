"""
Interpretation Router - Economic interpretation of FX signals
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any
import pandas as pd

from layer2.engine import DecisionEngine

router = APIRouter(prefix="/v1/fx", tags=["interpretation"])

_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = DecisionEngine()
    return _engine

@router.get("/interpretation")
async def get_interpretation(
    pair: str = Query(..., description="Currency pair, e.g. USD/JPY"),
    include_macro: bool = Query(False, description="Include macro context")
) -> Dict[str, Any]:
    """
    Obtiene interpretación económica de señales FX
    """
    try:
        engine = get_engine()
        
        # Obtener forecast
        forecast = engine.get_forecast(pair)
        
        # Construir interpretación básica
        direction = forecast.get("direction", "NEUTRAL")
        probability = forecast.get("probability", 0.5)
        confidence = forecast.get("confidence", 0.5)
        
        # Interpretación simple
        if probability > 0.6:
            strength = "strong"
        elif probability > 0.55:
            strength = "moderate"
        else:
            strength = "weak"
        
        interpretation = {
            "pair": pair,
            "timestamp": pd.Timestamp.now().isoformat(),
            "signal": {
                "direction": direction,
                "probability": probability,
                "confidence": confidence,
                "strength": strength
            },
            "narrative": f"El modelo indica una señal {direction.lower()} con {strength} convicción ({probability:.1%}) para {pair}.",
            "risks": [],
            "event_sensitivity": []
        }
        
        if include_macro:
            interpretation["macro_context"] = {
                "regime": "NEUTRAL",
                "summary": "Contexto macro no disponible"
            }
        
        return interpretation
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
