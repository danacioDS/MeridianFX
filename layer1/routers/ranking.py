from fastapi import APIRouter
from datetime import datetime
from ..models.responses import RankingResponse, RankedOpportunity
from layer2.ranking.engine import RankingEngine

router = APIRouter(prefix="/v1/fx", tags=["ranking"])
ranking_engine = RankingEngine()

@router.get("/ranking", response_model=RankingResponse)
async def get_ranking():
    data = ranking_engine.get_ranking()
    
    opportunities = []
    for opp in data['opportunities']:
        opportunities.append(
            RankedOpportunity(
                rank=opp.get('rank', 0),
                pair=opp['pair'],
                direction=opp.get('direction', 'UNKNOWN'),
                opportunity_score=opp.get('opportunity_score', 0.0),
                edge_ratio=opp.get('edge_ratio', 0.0),
                actionable=opp.get('actionable', False),
                confidence=opp.get('confidence', 0.0),
                decision_quality=opp.get('decision_quality', 'LOW'),
                position_size=opp.get('position_size', 0.0)
            )
        )
    
    return RankingResponse(
        timestamp=datetime.now(),
        opportunities=opportunities,
        top_opportunity=opportunities[0] if opportunities else None,
        total_actionable=data.get('total_actionable', 0),
        total_pairs=data.get('total_pairs', 0),
        snapshot_timestamp=datetime.now(),
        as_of=datetime.now()
    )
