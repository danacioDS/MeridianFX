from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from layer2.engine import DecisionEngine
from layer1.utils.pair_normalizer import normalize_pair
from layer1.adapters.decision_to_response import DecisionAdapter
import pandas as pd

router = APIRouter(prefix="/v1/fx", tags=["drivers"])

_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = DecisionEngine()
    return _engine

@router.get("/{pair}/drivers")
async def get_drivers(pair: str) -> Dict[str, Any]:
    """Obtener drivers SHAP y macro para un par"""
    try:
        engine = get_engine()
        
        # Normalizar par
        normalized_pair = normalize_pair(pair)
        
        # Obtener forecast (que incluye SHAP)
        forecast = engine.get_forecast(normalized_pair)
        
        # Extraer SHAP de forecast
        shap_data = forecast.get('shap') if forecast else None
        
        # Obtener feature importance del modelo si está disponible
        feature_importance = {}
        model = engine._get_model_for_pair(normalized_pair, "xgboost")
        if model is not None and hasattr(model, 'feature_importance'):
            try:
                importance_df = model.feature_importance()
                if importance_df is not None:
                    feature_importance = importance_df.to_dict()
            except Exception:
                pass
        
        # Si no hay feature_importance del modelo, usar SHAP contributions
        if not feature_importance and shap_data:
            contributions = shap_data.get('contributions', [])
            for c in contributions:
                feature = c.get('feature', '')
                contrib = c.get('abs_contribution', 0)
                if feature:
                    feature_importance[feature] = contrib
        
        # Formatear SHAP values según el contrato
        shap_values = []
        if shap_data:
            contributions = shap_data.get('contributions', [])
            # Ordenar por contribución absoluta (más importante primero)
            sorted_contrib = sorted(
                contributions,
                key=lambda x: abs(x.get('contribution', 0)),
                reverse=True
            )
            shap_values = [
                {
                    "feature": c.get("feature", "unknown"),
                    "contribution": round(c.get("contribution", 0), 4),
                    "abs_contribution": round(c.get("abs_contribution", 0), 4)
                }
                for c in sorted_contrib
            ]
        
        # Construir respuesta
        result = {
            "pair": normalized_pair,
            "timestamp": pd.Timestamp.now().isoformat(),
            "model_available": forecast.get('model', {}).get('type') != 'heuristic' if forecast else False,
            "model_version": forecast.get('model', {}).get('version', 'v1.0') if forecast else 'v1.0',
            "confidence": forecast.get("confidence", 0.5) if forecast else 0.5,
            "direction": forecast.get("direction", "NEUTRAL") if forecast else "NEUTRAL",
            "probability": forecast.get("probability", 0.5) if forecast else 0.5,
            "expected_return": forecast.get("expected_return", 0.0) if forecast else 0.0,
            "shap_values": shap_values,
            "feature_importance": feature_importance,
            "base_value": shap_data.get('base_value', 0.0) if shap_data else 0.0,
            "feature_count": shap_data.get('feature_count', 0) if shap_data else 0,
            "macro_regime": "NEUTRAL",
            "sentiment": {},
            "decision_quality": "MEDIUM"
        }
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
