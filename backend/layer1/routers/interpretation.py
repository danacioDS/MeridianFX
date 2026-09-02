import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from datetime import datetime

from layer1.llm.interpreter import EconomicInterpreter
from layer1.data.forecast_data import FORECAST_DATA

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/fx", tags=["interpretation"])

class InterpretationResponse(BaseModel):
    pair: str
    interpretation: List[str]
    context: Optional[dict] = None
    macro: Optional[dict] = None
    timestamp: str

# Interpreter global
_interpreter = None

def get_interpreter():
    global _interpreter
    if _interpreter is None:
        _interpreter = EconomicInterpreter()
    return _interpreter

@router.get("/interpretation")
async def get_interpretation(
    pair: str = Query(..., description="Par de divisas, ej: USD/JPY"),
    include_macro: bool = Query(False, description="Incluir datos macro en la respuesta"),
    interpreter: EconomicInterpreter = Depends(get_interpreter),
):
    """
    Obtiene interpretación del mercado para un par de divisas.
    """
    try:
        # Obtener datos de forecast para el par
        data = FORECAST_DATA.get(pair, FORECAST_DATA.get("USD/JPY", {})).copy()
        data["pair"] = pair
        
        # Construir contexto para el interpretador
        context = {
            "pair": pair,
            "direction": data.get("direction", "NEUTRAL"),
            "probability": data.get("probability", 0.5),
            "spot_price": data.get("spot", {}).get("price", 0),
            "change_pct": data.get("spot", {}).get("change_pct", 0),
            "forecasts": data.get("forecasts", {}),
            "volatility": data.get("volatility", 0),
            "regime": data.get("regime", "NEUTRAL"),
            "economic_filter": data.get("economic_filter", {}),
        }
        
        # Generar interpretación usando el LLM
        bullets = interpreter.interpret(context)
        
        # Respuesta
        response = {
            "pair": pair,
            "interpretation": bullets,
            "context": context,
            "timestamp": datetime.now().isoformat(),
        }
        
        # Incluir macro si se solicita
        if include_macro:
            try:
                from layer1.services.macro_service import get_macro_context
                macro_data = get_macro_context()
                response["macro"] = macro_data
            except Exception as e:
                logger.warning(f"Error getting macro data: {e}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating interpretation: {e}")
        return {
            "pair": pair,
            "interpretation": [
                f"Análisis en proceso para {pair}.",
                "El sistema está generando la interpretación.",
                "Por favor, intenta nuevamente en unos momentos."
            ],
            "context": {"pair": pair},
            "timestamp": datetime.now().isoformat()
        }
