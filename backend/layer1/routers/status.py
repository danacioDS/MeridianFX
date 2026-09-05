from fastapi import APIRouter
from datetime import datetime
from ..models.responses import StatusResponse, InfrastructureStatus, IntelligenceStatus, MetricsStatus
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from layer2.status.engine import StatusEngine

router = APIRouter(prefix="/v1", tags=["status"])

# Inicializar StatusEngine
status_engine = StatusEngine()

@router.get("/status", response_model=StatusResponse)
async def get_status():
    """Obtiene el estado real del sistema."""
    
    # Obtener estado completo
    full_status = status_engine.get_full_status()
    
    # Estado del sistema
    system = full_status.get("system", {})
    system_status = system.get("status", "HEALTHY")
    reason = system.get("reason", "All systems operational")
    
    # Modelos - estado de performance y drift
    models = full_status.get("models", [])
    active_models = [m for m in models if m.get("active")]
    stale_models = [m for m in models if m.get("status") == "stale"]
    
    model_performance_status = "STABLE"
    if len(stale_models) > len(models) / 2:
        model_performance_status = "DEGRADED"
    elif len(active_models) == 0:
        model_performance_status = "ERROR"
    
    model_drift_status = "NONE"
    if len(stale_models) > 0:
        model_drift_status = "WARNING"
    if len(stale_models) > len(models) / 2:
        model_drift_status = "CRITICAL"
    
    # Fuentes de datos
    data_sources = full_status.get("data_sources", [])
    data_quality_status = "FRESH"
    data_quality_overall = "GOOD"
    
    offline_sources = [s for s in data_sources if s.get("status") == "offline"]
    if len(offline_sources) > 0:
        data_quality_status = "DEGRADED"
        data_quality_overall = "DEGRADED"
    if len(offline_sources) == len(data_sources):
        data_quality_status = "STALE"
        data_quality_overall = "POOR"
    
    # Decision validity
    decision_validity_status = "VALID"
    if system_status == "DEGRADED":
        decision_validity_status = "DEGRADED"
    if system_status == "ERROR":
        decision_validity_status = "INVALID"
    
    # Safe mode state
    safe_mode_state = "INACTIVE"
    if len(offline_sources) > len(data_sources) / 2:
        safe_mode_state = "ACTIVE"
    
    # Infraestructura
    infrastructure = InfrastructureStatus(
        api="HEALTHY",
        database="NOT_CONFIGURED",  # TODO: conectar a DB real
        pipeline="HEALTHY",
        cache=full_status.get("cache", {}).get("status", "HEALTHY")
    )
    
    # Intelligence
    intelligence = IntelligenceStatus(
        data_quality={'status': data_quality_status, 'overall': data_quality_overall},
        model_performance={'status': model_performance_status},
        model_drift={'status': model_drift_status},
        decision_validity={'status': decision_validity_status},
        safe_mode_state=safe_mode_state
    )
    
    # Métricas
    cache_status = full_status.get("cache", {})
    metrics = MetricsStatus(
        data_freshness=data_quality_status,
        prediction_coverage=len(active_models) / len(models) if models else 1.0
    )
    
    return StatusResponse(
        system_status=system_status,
        reason=reason,
        timestamp=datetime.now(),
        infrastructure=infrastructure,
        intelligence=intelligence,
        metrics=metrics
    )
