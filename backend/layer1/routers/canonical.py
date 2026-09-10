"""
Endpoint canónico que usa el DecisionPipeline.
"""

from fastapi import APIRouter, HTTPException
from backend.layer2.pipeline_bridge import PipelineBridge
from backend.src.meridian_fx.decision.pipeline import DecisionPipeline
from backend.src.meridian_fx.decision.validation.validate_integration import (
    FakeFeatureStore, FakeDataQualityRegistry, FakeFreshnessRegistry, FakeDriftRegistry
)

router = APIRouter(tags=["canonical"])

# Inicializar pipeline (usando fake providers por ahora)
pipeline = DecisionPipeline(
    feature_store=FakeFeatureStore(vix=15.0),
    data_quality_registry=FakeDataQualityRegistry(0.90),
    freshness_registry=FakeFreshnessRegistry(3.0),
    drift_registry=FakeDriftRegistry(0.05)
)

bridge = PipelineBridge(pipeline)

@router.get("/{pair:path}/decision")
async def get_canonical_decision(pair: str, horizon_days: int = 30):
    """
    Obtiene decisión del pipeline canónico.
    """
    try:
        # Ahora es async
        result = await bridge.evaluate_pair(pair, horizon_days)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{pair:path}/risk")
async def get_canonical_risk(pair: str, horizon_days: int = 30):
    """
    Obtiene el Risk Assessment canónico para un par.
    """
    try:
        result = await bridge.evaluate_pair(pair, horizon_days)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return {
            "pair": pair,
            "horizon_days": horizon_days,
            "risk": result.get("risk"),
            "macro_data_status": result.get("macro_data_status"),
            "decision_summary": {
                "actionable": (result.get("decision") or {}).get("actionable"),
                "signal_validity": (result.get("decision") or {}).get("signal_validity"),
                "direction": (result.get("decision") or {}).get("direction"),
                "edge_ratio": (result.get("decision") or {}).get("edge_ratio"),
            },
            "timestamp": result.get("timestamp"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

