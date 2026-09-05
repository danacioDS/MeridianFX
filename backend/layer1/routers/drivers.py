from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging
import pandas as pd

logger = logging.getLogger(__name__)

router = APIRouter(tags=["drivers"])

_engine = None

def get_engine():
    global _engine
    if _engine is None:
        from backend.layer2.engine import DecisionEngine
        _engine = DecisionEngine()
    return _engine

@router.get("/{base}/{quote}/drivers")
async def get_drivers(base: str, quote: str) -> Dict[str, Any]:
    """Obtener drivers SHAP y macro para un par"""
    pair = f"{base}/{quote}"
    
    try:
        from backend.layer2.engine import DecisionEngine
        from backend.layer1.utils.pair_normalizer import normalize_pair
        
        engine = get_engine()
        normalized_pair = normalize_pair(pair)
        
        logger.info(f"Requesting drivers for pair: {normalized_pair}")
        
        # Verificar si el modelo existe
        model = engine._get_model_for_pair(normalized_pair, "xgboost")
        if model is None:
            logger.warning(f"Model not found for {normalized_pair}")
            raise HTTPException(status_code=404, detail=f"Model not found for {pair}")
        
        # Obtener forecast (que incluye SHAP)
        forecast = engine.get_forecast(normalized_pair)
        
        # Extraer SHAP del forecast si existe
        shap_data = forecast.get('shap') if forecast else None
        
        # Construir drivers
        drivers = []
        base_value = 0.0
        feature_count = 0
        
        if shap_data:
            contributions = shap_data.get('contributions', [])
            sorted_contrib = sorted(
                contributions,
                key=lambda x: abs(x.get('contribution', 0)),
                reverse=True
            )
            drivers = [
                {
                    "feature": c.get("feature", "unknown"),
                    "contribution": round(c.get("contribution", 0), 4),
                    "abs_contribution": round(c.get("abs_contribution", 0), 4)
                }
                for c in sorted_contrib
            ]
            base_value = shap_data.get('base_value', 0.0)
            feature_count = len(shap_data.get('contributions', []))
        
        # Macro drivers (ejemplo con datos de mercado)
        macro_drivers = [
            {
                "name": "VIX",
                "value": 16.8,
                "description": "Volatility Index",
                "direction": "risk-off" if 16.8 > 20 else "risk-on"
            },
            {
                "name": "Risk Appetite",
                "value": 72.0,
                "description": "Market risk appetite",
                "direction": "high" if 72.0 > 50 else "low"
            },
            {
                "name": "Regime",
                "value": "RISK_ON",
                "description": "Market regime",
                "direction": "neutral"
            }
        ]
        
        # Construir respuesta completa
        result = {
            "pair": pair,
            "normalized_pair": normalized_pair,
            "model_available": True,
            "model_type": "xgboost",
            "timestamp": pd.Timestamp.now().isoformat(),
            "drivers": drivers,
            "macro_drivers": macro_drivers,
            "base_value": base_value,
            "feature_count": feature_count
        }
        
        # Incluir forecast si existe
        if forecast:
            result["forecast"] = {
                "direction": forecast.get("direction", "NEUTRAL"),
                "probability": forecast.get("probability", 0.5),
                "expected_return": forecast.get("expected_return", 0.0),
                "confidence": forecast.get("confidence", 0.5)
            }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in drivers endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
