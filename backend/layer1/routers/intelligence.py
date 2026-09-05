"""
Market Intelligence Router
--------------------------
Synthesizes existing MeridianFX research and decision outputs
into an English market-intelligence response.

Architecture:
Data -> Research -> Decision -> Intelligence
"""

from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import APIRouter

from backend.layer2.ranking.engine import RankingEngine


router = APIRouter(tags=["intelligence"])

# Reuse the existing ranking engine as the source of truth
ranking_engine = RankingEngine()


def _direction_label(direction: str) -> str:
    if direction == "UP":
        return "bullish"
    if direction == "DOWN":
        return "bearish"
    return "neutral"


def _build_context(ranking: Dict[str, Any]) -> Dict[str, Any]:
    opportunities = ranking.get("opportunities", [])

    actionable = [
        item for item in opportunities
        if item.get("actionable", False)
    ]

    if actionable:
        context = (
            f"The current MeridianFX decision layer identifies "
            f"{len(actionable)} actionable opportunity "
            f"{'across the monitored FX universe' if len(actionable) > 1 else 'in the monitored FX universe'}."
        )
    else:
        context = (
            "The current MeridianFX decision layer remains selective. "
            "No monitored opportunity currently satisfies the full economic "
            "criteria required for an actionable signal."
        )

    return {
        "market_coverage": len(opportunities),
        "actionable_opportunities": len(actionable),
        "context": context,
    }


def _build_signals(ranking: Dict[str, Any]) -> List[Dict[str, Any]]:
    opportunities = ranking.get("opportunities", [])

    signals = []

    for opportunity in opportunities[:5]:
        pair = opportunity.get("pair", "UNKNOWN")
        direction = opportunity.get("direction", "NEUTRAL")
        probability = opportunity.get("confidence", 0.0)
        edge_ratio = opportunity.get("edge_ratio", 0.0)
        score = opportunity.get("opportunity_score", 0.0)

        signals.append(
            {
                "pair": pair,
                "direction": _direction_label(direction),
                "confidence": round(probability, 4),
                "edge_ratio": round(edge_ratio, 4),
                "opportunity_score": round(score, 4),
                "actionable": opportunity.get("actionable", False),
            }
        )

    return signals


def _build_interpretation(ranking: Dict[str, Any]) -> List[str]:
    opportunities = ranking.get("opportunities", [])

    if not opportunities:
        return [
            "No model-ranked opportunities are currently available.",
            "The intelligence layer cannot establish a directional market view "
            "without valid research outputs.",
        ]

    top = opportunities[0]

    pair = top.get("pair", "UNKNOWN")
    direction = _direction_label(top.get("direction", "NEUTRAL"))
    confidence = top.get("confidence", 0.0)
    edge = top.get("edge_ratio", 0.0)
    actionable = top.get("actionable", False)

    interpretation = [
        (
            f"The highest-ranked signal is {pair}, with a {direction} bias "
            f"and a decision confidence of {confidence * 100:.1f}%."
        ),
        (
            f"Its economic edge is {edge:.2f}x, which indicates how strongly "
            "the expected opportunity compares with the decision threshold."
        ),
    ]

    if actionable:
        interpretation.append(
            "The decision layer considers the leading signal economically actionable."
        )
    else:
        interpretation.append(
            "The leading signal is not currently actionable, indicating that "
            "model direction alone is insufficient to justify exposure."
        )

    return interpretation


def _build_decision_view(ranking: Dict[str, Any]) -> Dict[str, Any]:
    opportunities = ranking.get("opportunities", [])

    actionable_count = sum(
        1 for item in opportunities
        if item.get("actionable", False)
    )

    return {
        "status": "ACTIONABLE" if actionable_count > 0 else "SELECTIVE",
        "actionable_count": actionable_count,
        "total_pairs": len(opportunities),
        "principle": (
            "Prediction is not equivalent to a trading decision. "
            "MeridianFX requires economic edge and decision validity "
            "before classifying a signal as actionable."
        ),
    }


def _build_summary(
    ranking: Dict[str, Any],
    context: Dict[str, Any],
) -> str:
    opportunities = ranking.get("opportunities", [])

    if not opportunities:
        return (
            "MeridianFX currently has insufficient ranked research signals "
            "to produce a reliable market-intelligence view."
        )

    top = opportunities[0]
    pair = top.get("pair", "UNKNOWN")
    direction = _direction_label(top.get("direction", "NEUTRAL"))
    actionable = top.get("actionable", False)

    if actionable:
        return (
            f"MeridianFX identifies {pair} as the leading {direction} opportunity. "
            "The signal passes the current economic decision criteria and "
            "therefore warrants further evaluation for exposure."
        )

    return (
        f"MeridianFX currently identifies {pair} as the leading {direction} signal, "
        "but the decision layer does not classify it as actionable. "
        "The current environment therefore favors selectivity over aggressive exposure."
    )


@router.get("/market-intelligence")
async def get_market_intelligence() -> Dict[str, Any]:
    """
    Generate a deterministic market-intelligence synthesis
    from the existing MeridianFX ranking engine.
    """

    ranking = ranking_engine.get_ranking()

    context = _build_context(ranking)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "system": "MeridianFX",
        "language": "en",
        "architecture": {
            "data": "market and macroeconomic observations",
            "research": "model forecasts and ranked opportunities",
            "decision": "economic edge and actionability",
            "intelligence": "contextual synthesis",
        },
        "current_context": context,
        "key_signals": _build_signals(ranking),
        "model_interpretation": _build_interpretation(ranking),
        "decision_view": _build_decision_view(ranking),
        "summary": _build_summary(ranking, context),
        "source": {
            "ranking_engine": "backend.layer2.ranking.engine.RankingEngine",
            "total_pairs": ranking.get("total_pairs", 0),
            "total_actionable": ranking.get("total_actionable", 0),
        },
    }
