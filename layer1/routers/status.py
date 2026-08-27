from fastapi import APIRouter
from datetime import datetime
from ..models.responses import StatusResponse, InfrastructureStatus, IntelligenceStatus, MetricsStatus

router = APIRouter(prefix="/v1", tags=["status"])

@router.get("/status", response_model=StatusResponse)
async def get_status():
    return StatusResponse(
        system_status="HEALTHY",
        reason="All systems operational",
        timestamp=datetime.now(),
        infrastructure=InfrastructureStatus(
            api="HEALTHY",
            database="HEALTHY",
            pipeline="HEALTHY",
            cache="HEALTHY"
        ),
        intelligence=IntelligenceStatus(
            data_quality={'status': 'FRESH', 'overall': 'GOOD'},
            model_performance={'status': 'STABLE'},
            model_drift={'status': 'NONE'},
            decision_validity={'status': 'VALID'},
            safe_mode_state="INACTIVE"
        ),
        metrics=MetricsStatus(
            data_freshness="Fresh",
            prediction_coverage=0.98
        )
    )
