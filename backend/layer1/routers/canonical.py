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
