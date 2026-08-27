from fastapi import APIRouter
from datetime import datetime
from ..models.responses import RankingResponse
from ..adapters.decision_to_response import DecisionAdapter

router = APIRouter(prefix="/v1/fx", tags=["ranking"])

@router.get("/ranking", response_model=RankingResponse)
async def get_ranking():
    mock_data = {
        'opportunities': [
            {'rank': 1, 'pair': 'USD/JPY', 'direction': 'UP', 'opportunity_score': 0.85, 'edge_ratio': 3.1, 'actionable': True, 'confidence': 0.72, 'decision_quality': 'HIGH', 'position_size': 0.15},
            {'rank': 2, 'pair': 'EUR/USD', 'direction': 'DOWN', 'opportunity_score': 0.72, 'edge_ratio': 2.4, 'actionable': True, 'confidence': 0.65, 'decision_quality': 'MEDIUM', 'position_size': 0.10},
            {'rank': 3, 'pair': 'GBP/USD', 'direction': 'UP', 'opportunity_score': 0.58, 'edge_ratio': 1.8, 'actionable': False, 'confidence': 0.45, 'decision_quality': 'LOW', 'position_size': 0.0}
        ]
    }
    return DecisionAdapter.to_ranking_response(mock_data)
