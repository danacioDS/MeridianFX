from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from layer2.engine import DecisionEngine

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
        result = engine.get_drivers(pair)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
