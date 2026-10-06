from fastapi import APIRouter, HTTPException
from datetime import datetime
from backend.layer2.engine import DecisionEngine

router = APIRouter(tags=["forecast"])

@router.get("/{base}/{quote}/forecast")
async def get_forecast(base: str, quote: str):
    """
    Obtener forecast real del modelo Logistic_24 para un par específico.
    """
    pair = f"{base}/{quote}"

    try:
        engine = DecisionEngine()
        forecast = engine.get_forecast(pair)

        # Si el forecast es fallback/neutral, devolver error 404
        if forecast.get("model", {}).get("type") == "fallback":
            raise HTTPException(
                status_code=404,
                detail=f"No se pudo generar forecast para {pair}"
            )

        # Mapear al formato esperado por el frontend
        return {
            "pair": pair,
            "prediction": {
                "direction": forecast.get("direction", "NEUTRAL"),
                "probability": forecast.get("probability", 0.5),
                "expected_return": forecast.get("expected_return", 0.0),
                "expected_volatility": forecast.get("expected_volatility", 0.0),
            },
            "decision": {
                "actionable": forecast.get("actionable", False),
                "direction": forecast.get("direction", "NEUTRAL"),
                "confidence": forecast.get("confidence", 0.0),
                "edge_ratio": forecast.get("edge_ratio", 0.0),
                "net_return": forecast.get("net_return", 0.0),
                "position_size": forecast.get("position_size", 0.0),
                # 2026-10-06: propagar la provenance del modelo. El engine
                # la calcula del promotion_status del artefacto canónico.
                "signal_validity": forecast.get("signal_validity", "UNAVAILABLE"),
                "forecast_eligibility": forecast.get("forecast_eligibility", "unavailable"),
            },
            "lineage": {
                "model": {
                    "version": "v1.0",
                    "type": "logistic",
                    "promotion_status": forecast.get("model", {}).get("promotion_status"),
                    "val_auc": forecast.get("model", {}).get("val_auc"),
                    "val_std": forecast.get("model", {}).get("val_std"),
                    "bal_acc": forecast.get("model", {}).get("bal_acc"),
                }
            },
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
