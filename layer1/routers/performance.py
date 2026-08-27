from fastapi import APIRouter, Path, Query
from datetime import datetime
from typing import Optional
from ..models.responses import PerformanceResponse
from ..adapters.decision_to_response import DecisionAdapter

router = APIRouter(prefix="/v1/fx", tags=["performance"])

@router.get("/performance/{pair:path}", response_model=PerformanceResponse)
async def get_performance(
    pair: str = Path(..., description="Currency pair (e.g., USD/JPY)"),
    period: Optional[str] = Query("1y", description="Performance period (1m, 3m, 6m, 1y)")
):
    mock_data = {
        'directional_accuracy': 0.62,
        'auc': 0.71,
        'brier_score': 0.18,
        'ece': 0.04,
        'log_loss': 0.52,
        'sharpe_ratio': 1.42,
        'sharpe_net': 1.28,
        'max_drawdown': -0.085,
        'profit_factor': 1.53,
        'win_rate': 0.58,
        'total_return': 0.124,
        'regime_performance': [
            {'regime': 'RISK_ON', 'return_value': 0.08, 'count': 45},
            {'regime': 'RISK_OFF', 'return_value': 0.04, 'count': 30}
        ],
        'current_sharpe': 1.35,
        'historical_sharpe': 1.42,
        'drift_detected': False,
        'drift_severity': 'none'
    }
    return DecisionAdapter.to_performance_response(mock_data, pair)
