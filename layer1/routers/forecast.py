from fastapi import APIRouter, Path
from datetime import datetime
from ..models.responses import ForecastResponse
from ..adapters.decision_to_response import DecisionAdapter
from layer2.engine import DecisionEngine

# Inicializar motor de decisión
engine = DecisionEngine()

router = APIRouter(prefix="/v1/fx", tags=["forecast"])

@router.get("/{pair:path}/forecast", response_model=ForecastResponse)
async def get_forecast(
    pair: str = Path(..., description="Currency pair (e.g., USD/JPY)")
):
    """Obtener forecast para un par de divisas usando Layer 2 real."""
    # Obtener decisión de Layer 2
    decision_data = engine.get_forecast(pair)
    return DecisionAdapter.to_forecast_response(decision_data, pair)
