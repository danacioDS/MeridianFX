"""
Market Intelligence Router
--------------------------
Synthesizes existing MeridianFX research and decision outputs
into an English market-intelligence response.

Architecture:
Data -> Research -> Decision -> Intelligence
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Query

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
            f"The decision layer has identified {len(actionable)} actionable "
            f"opportunity"
            f"{'ies' if len(actionable) > 1 else ''} "
            f"across the monitored FX universe. An actionable signal "
            f"means: the model has a directional view, the expected return "
            f"after costs (net return) is large enough to exceed the "
            f"required minimum edge, and all hard gates have passed."
        )
    else:
        context = (
            "The MeridianFX decision layer is currently SELECTIVE. This "
            "means the system has evaluated every pair in the monitored "
            "universe and found that none currently satisfies the full "
            "set of economic criteria required for an actionable signal. "
            "In practical terms: a model may have a directional view, but "
            "the expected profit after transaction costs is not large "
            "enough, relative to the required minimum edge, to justify "
            "exposure. The system therefore prefers no position over a "
            "marginal one."
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


def _build_selected_pair_view(
    ranking: Dict[str, Any],
    pair: str,
) -> Optional[Dict[str, Any]]:
    """
    Build a pair-focused view for the selected pair.

    Returns None if the pair is not present in the ranking.
    """
    opportunities = ranking.get("opportunities", [])

    if not opportunities:
        return None

    # Find the selected pair in the ranking
    selected = next(
        (o for o in opportunities if o.get("pair") == pair),
        None,
    )

    if selected is None:
        return {
            "pair": pair,
            "available": False,
            "reason": "PAIR_NOT_IN_RANKING",
            "narrative": (
                f"{pair} is not part of the monitored ranking universe. "
                f"The ranking currently tracks {len(opportunities)} pair(s) "
                f"that passed the registry promotion gate. The canonical "
                f"Decision pipeline still evaluates this pair separately."
            ),
        }

    direction = selected.get("direction", "NEUTRAL")
    direction_label = _direction_label(direction)
    confidence = selected.get("confidence", 0.0)
    edge_ratio = selected.get("edge_ratio", 0.0)
    actionable = selected.get("actionable", False)
    quality = selected.get("decision_quality", "LOW")
    rank = selected.get("rank", None)

    # Narrative depends on the state
    if actionable:
        narrative = (
            f"{pair} passes the economic filter. "
            f"Direction: {direction_label}, confidence {confidence * 100:.1f}%, "
            f"edge {edge_ratio:.2f}x."
        )
        status = "ACTIONABLE"
    elif edge_ratio == 0 and confidence == 0:
        narrative = (
            f"{pair} is not actionable. Edge {edge_ratio:.2f}x is below the "
            f"threshold. The rest of the universe remains SELECTIVE."
        )
        status = "NOT_ACTIONABLE"
    else:
        narrative = (
            f"{pair} is not actionable. Edge {edge_ratio:.2f}x is below the "
            f"threshold. The FX market remains SELECTIVE — no pair "
            f"currently exceeds the economic filter."
        )
        status = "NOT_ACTIONABLE"

    return {
        "pair": pair,
        "available": True,
        "status": status,
        "rank": rank,
        "direction": direction,
        "direction_label": direction_label,
        "confidence": round(confidence, 4),
        "edge_ratio": round(edge_ratio, 4),
        "opportunity_score": round(selected.get("opportunity_score", 0.0), 4),
        "quality": quality,
        "actionable": actionable,
        "narrative": narrative,
    }




def _build_interpretation_for_pair(
    ranking: Dict[str, Any],
    pair: str,
) -> List[str]:
    """Build model_interpretation focused on the selected pair."""
    opportunities = ranking.get("opportunities", [])

    if not opportunities:
        return _build_interpretation(ranking)

    selected = next(
        (o for o in opportunities if o.get("pair") == pair),
        None,
    )

    if selected is None:
        return [
            f"{pair} is not part of the monitored ranking universe.",
            "The ranking currently tracks only pairs that passed the "
            "registry promotion gate. The canonical Decision pipeline "
            "still evaluates this pair separately.",
        ]

    direction = _direction_label(selected.get("direction", "NEUTRAL"))
    confidence = selected.get("confidence", 0.0)
    edge = selected.get("edge_ratio", 0.0)
    actionable = selected.get("actionable", False)
    rank = selected.get("rank", None)
    quality = selected.get("decision_quality", "LOW")

    interpretation = [
        f"{pair} is classified as "
        f"{'ACTIONABLE' if actionable else 'NOT ACTIONABLE'}.",
        f"Direction: {direction}, confidence {confidence * 100:.1f}%, "
        f"quality {quality}.",
        f"Edge: {edge:.2f}x.",
    ]

    if actionable:
        interpretation.append(
            "The signal passes the economic filter and warrants further "
            "evaluation for exposure."
        )
    else:
        interpretation.append(
            "The signal does not exceed the economic threshold. The rest "
            "of the universe remains SELECTIVE."
        )

    if rank is not None:
        interpretation.append(
            f"Ranking: position #{rank} of {len(opportunities)} monitored "
            f"pairs."
        )

    return interpretation


def _build_signals_for_pair(
    ranking: Dict[str, Any],
    pair: str,
) -> List[Dict[str, Any]]:
    """Build key_signals with the selected pair first."""
    opportunities = ranking.get("opportunities", [])

    if not opportunities:
        return []

    selected = next(
        (o for o in opportunities if o.get("pair") == pair),
        None,
    )

    ordered = []
    if selected is not None:
        ordered.append(selected)
    for opp in opportunities:
        if opp.get("pair") != pair and len(ordered) < 5:
            ordered.append(opp)

    signals = []
    for opportunity in ordered[:5]:
        pair_name = opportunity.get("pair", "UNKNOWN")
        direction = opportunity.get("direction", "NEUTRAL")
        probability = opportunity.get("confidence", 0.0)
        edge_ratio = opportunity.get("edge_ratio", 0.0)
        score = opportunity.get("opportunity_score", 0.0)

        signals.append(
            {
                "pair": pair_name,
                "direction": _direction_label(direction),
                "confidence": round(probability, 4),
                "edge_ratio": round(edge_ratio, 4),
                "opportunity_score": round(score, 4),
                "actionable": opportunity.get("actionable", False),
                "is_selected": pair_name == pair,
            }
        )

    return signals


def _build_summary_for_pair(
    ranking: Dict[str, Any],
    pair: str,
    fallback_summary: str,
) -> str:
    """Build a summary focused on the selected pair."""
    opportunities = ranking.get("opportunities", [])

    if not opportunities:
        return fallback_summary

    selected = next(
        (o for o in opportunities if o.get("pair") == pair),
        None,
    )

    if selected is None:
        return (
            f"{pair} is not part of the monitored ranking universe. "
            f"The ranking currently tracks only pairs that passed the "
            f"registry promotion gate. See the Decision page for the "
            f"canonical evaluation of this pair."
        )

    direction = _direction_label(selected.get("direction", "NEUTRAL"))
    confidence = selected.get("confidence", 0.0)
    edge = selected.get("edge_ratio", 0.0)
    actionable = selected.get("actionable", False)

    if actionable:
        return (
            f"{pair} passes the economic filter with direction {direction}, "
            f"confidence {confidence * 100:.1f}%, and edge {edge:.2f}x. "
            f"It warrants further evaluation for exposure."
        )

    return (
        f"{pair} is not actionable. Direction: {direction}, "
        f"confidence {confidence * 100:.1f}%, edge {edge:.2f}x. "
        f"The rest of the universe remains SELECTIVE."
    )


@router.get("/market-intelligence")
async def get_market_intelligence(
    pair: Optional[str] = Query(None, description="Optional FX pair to focus on"),
) -> Dict[str, Any]:
    """
    Generate a deterministic market-intelligence synthesis
    from the existing MeridianFX ranking engine.

    If `pair` is provided, adds a `selected_pair_view` block that focuses
    on that pair while keeping the system-wide context intact.
    """

    ranking = ranking_engine.get_ranking()

    context = _build_context(ranking)

    # Global blocks (always computed)
    base_summary = _build_summary(ranking, context)
    base_interpretation = _build_interpretation(ranking)
    base_signals = _build_signals(ranking)

    # If a pair is selected, focus interpretation and signals on it
    if pair:
        focused_interpretation = _build_interpretation_for_pair(ranking, pair)
        focused_signals = _build_signals_for_pair(ranking, pair)
        focused_summary = _build_summary_for_pair(ranking, pair, base_summary)
    else:
        focused_interpretation = base_interpretation
        focused_signals = base_signals
        focused_summary = base_summary

    response: Dict[str, Any] = {
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
        "key_signals": focused_signals,
        "model_interpretation": focused_interpretation,
        "decision_view": _build_decision_view(ranking),
        "summary": focused_summary,
        "source": {
            "ranking_engine": "backend.layer2.ranking.engine.RankingEngine",
            "total_pairs": ranking.get("total_pairs", 0),
            "total_actionable": ranking.get("total_actionable", 0),
        },
    }

    if pair:
        selected = _build_selected_pair_view(ranking, pair)
        if selected is not None:
            response["selected_pair_view"] = selected

    return response
