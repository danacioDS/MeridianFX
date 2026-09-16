"""
Ranking endpoint — versión canónica.

Reemplaza el RankingEngine legacy (XGBoost + registry.json) por una vista
agregada del pipeline canónico (Logistic_24 + KI-009).

Los 9 pares del universo canónico se evalúan con la misma lógica que
/canonical/{pair}/decision, garantizando consistencia entre ambos endpoints.

Historia:
  - Antes: /v1/fx/ranking usaba RankingEngine legacy que iteraba sobre
    ModelRegistry + XGBoost. Tras el promotion gate (v2.5.1+, MIN_AUC=0.52,
    MIN_N_SAMPLES=300) solo USD/CHF pasó el gate, y el ranking colapsó a 1 par.
  - Ahora: /v1/fx/ranking usa PipelineBridge + Logistic_24 (9 pares). Los pares
    RESTRICTED por KI-009 se incluyen con actionable=False, confidence=0.0.
"""
import asyncio
from datetime import datetime
from typing import Optional

from fastapi import APIRouter

from ..models.responses import RankingResponse, RankedOpportunity
from backend.layer1.dependencies import bridge

router = APIRouter(tags=["ranking"])

# Universo canónico de 9 pares (mismo que CANONICAL_FX_PAIRS en frontend)
CANONICAL_FX_PAIRS = [
    "USD/JPY",
    "EUR/USD",
    "GBP/USD",
    "USD/CNY",
    "USD/MXN",
    "USD/BRL",
    "USD/ARS",
    "USD/BOB",
    "USD/CHF",
]

# El contrato legacy del frontend usa "UP"/"DOWN"/"NEUTRAL".
# Decision.direction usa Direction.LONG/SHORT/NEUTRAL (StrEnum).
# Mapeo para no romper el contrato del frontend.
_RAW_TO_DISPLAY_DIRECTION = {
    "LONG": "UP",
    "SHORT": "DOWN",
    "NEUTRAL": "NEUTRAL",
}


async def _evaluate_pair_for_ranking(pair: str) -> Optional[dict]:
    """Evalúa un par con el pipeline canónico y lo formatea para el ranking."""
    try:
        result = await bridge.evaluate_pair(pair, horizon_days=5)
    except Exception as e:
        print(f"⚠️ Ranking: error evaluando {pair}: {e}")
        return None

    if not result or "error" in result:
        return None

    decision = result.get("decision") or {}

    probability = decision.get("confidence", 0.0) or 0.0
    edge_ratio = decision.get("edge_ratio", 0.0) or 0.0
    actionable = bool(decision.get("actionable", False))
    raw_direction = decision.get("direction", "NEUTRAL")
    direction = _RAW_TO_DISPLAY_DIRECTION.get(raw_direction, "NEUTRAL")
    position_size = decision.get("position_size", 0.0) or 0.0

    # opportunity_score: misma fórmula que el ranking legacy
    opportunity_score = (probability * 0.6) + (min(edge_ratio / 3.0, 1.0) * 0.4)
    opportunity_score = min(max(opportunity_score, 0.0), 1.0)

    if probability > 0.7:
        decision_quality = "HIGH"
    elif probability > 0.4:
        decision_quality = "MEDIUM"
    else:
        decision_quality = "LOW"

    return {
        "pair": pair,
        "direction": direction,
        "opportunity_score": opportunity_score,
        "edge_ratio": edge_ratio,
        "actionable": actionable,
        "confidence": probability,
        "decision_quality": decision_quality,
        "position_size": position_size,
    }


@router.get("/ranking", response_model=RankingResponse)
async def get_ranking():
    """
    Ranking canónico: evalúa los 9 pares del universo con Logistic_24 + KI-009.

    Los pares RESTRICTED por el gate de régimen (KI-009) se incluyen con
    actionable=False y confidence=0.0 para reflejar que están monitoreados
    pero no son elegibles para pronóstico direccional.
    """
    tasks = [_evaluate_pair_for_ranking(pair) for pair in CANONICAL_FX_PAIRS]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    opportunities = [
        r for r in results
        if isinstance(r, dict) and r is not None
    ]

    opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)
    for i, opp in enumerate(opportunities):
        opp["rank"] = i + 1

    ranked = [RankedOpportunity(**opp) for opp in opportunities]

    return RankingResponse(
        timestamp=datetime.now(),
        opportunities=ranked,
        top_opportunity=ranked[0] if ranked else None,
        total_actionable=sum(1 for o in ranked if o.actionable),
        total_pairs=len(ranked),
        snapshot_timestamp=datetime.now(),
        as_of=datetime.now(),
    )
