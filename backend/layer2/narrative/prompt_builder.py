"""
Prompt builder for narrative generation.

Computes the narrative_key (stable identity) and builds the prompts
for the LLM. The narrative_key changes ONLY when the logical state
of the decision changes.
"""
from __future__ import annotations

import hashlib
from typing import Any, Dict


PROMPT_VERSION = "v1"


def compute_narrative_key(decision_result: Dict[str, Any]) -> str:
    """
    Compute a stable identity for the decision.

    The five groups that define the decision:
      - WHO DECIDED:      pair, horizon_days
      - WHAT WAS DECIDED: direction, signal_validity, actionable
      - WITH WHAT EVIDENCE: edge_ratio, net_return
      - WITH WHAT MODEL:  model_id, model_version
      - WITH WHAT DATA:   dataset_id, feature_version, macro_status

    It does NOT change on repeated calls with the same logical decision.
    """
    d = decision_result.get("decision") or {}
    a = decision_result.get("artifact") or {}
    e = decision_result.get("economic") or {}
    m = decision_result.get("macro_data_status") or {}

    fingerprint = (
        # WHO DECIDED
        f"{d.get('pair', '')}|"
        f"{d.get('horizon_days', 0)}|"
        # WHAT WAS DECIDED
        f"{d.get('direction', '')}|"
        f"{d.get('signal_validity', '')}|"
        f"{d.get('actionable', False)}|"
        # WITH WHAT EVIDENCE
        f"{e.get('edge_ratio', 0.0):.4f}|"
        f"{e.get('net_return', 0.0):.4f}|"
        # WITH WHAT MODEL
        f"{a.get('model_id', '')}|"
        f"{a.get('model_version', '')}|"
        # WITH WHAT DATA
        f"{a.get('dataset_id', '')}|"
        f"{a.get('feature_version', '')}|"
        f"{m.get('status', '')}"
    )
    return hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:16]


def _fmt_bps(value: float | None) -> str:
    if value is None:
        return "—"
    return f"{value:.2f} bps"


def _fmt_pct(value: float | None) -> str:
    if value is None:
        return "—"
    return f"{value * 100:.2f}%"


def _fmt_ratio(value: float | None) -> str:
    if value is None:
        return "—"
    return f"{value:.2f}×"


def build_system_prompt() -> str:
    return """You are a financial analyst writing a short, clear explanation
of a quantitative decision for a non-technical audience.

RULES:
- Use plain English.
- Explain any technical term (ACTIONABLE, DEGRADED, edge ratio, bps).
- Write 2-3 paragraphs separated by a blank line.
- Do NOT recommend any action.
- Do NOT use the words "buy" or "sell".
- Do NOT invent data. Use only what is provided.
- Be direct and informative, not promotional."""


def build_user_prompt(decision_result: Dict[str, Any]) -> str:
    d = decision_result.get("decision") or {}
    a = decision_result.get("artifact") or {}
    e = decision_result.get("economic") or {}
    c = decision_result.get("costs") or {}
    q = decision_result.get("quality") or {}
    r = decision_result.get("risk") or {}
    g = decision_result.get("gate") or {}
    m = decision_result.get("macro_data_status") or {}
    s = decision_result.get("signals") or {}

    def _score(obj, key):
        """Read a score component from either a dict or a Pydantic object."""
        if obj is None:
            return "—"
        if isinstance(obj, dict):
            v = obj.get(key)
        else:
            v = getattr(obj, key, None)
        if v is None:
            return "—"
        if isinstance(v, dict):
            return v.get("value", "—")
        return getattr(v, "value", v)

    lines = [
        f"PAIR: {d.get('pair', 'UNKNOWN')}",
        f"HORIZON: {d.get('horizon_days', 0)} days",
        "",
        "DECISION:",
        f"- Direction: {d.get('direction', 'UNKNOWN')}",
        f"- Confidence: {_fmt_pct(d.get('confidence'))}",
        f"- Actionable: {'YES' if d.get('actionable') else 'NO'}",
        f"- Signal validity: {d.get('signal_validity', 'UNKNOWN')}",
        f"- Rejection reason: {d.get('rejection_reason') or 'none'}",
        "",
        "ECONOMIC ANALYSIS:",
        f"- Gross return: {_fmt_bps(e.get('directional_gross_return'))}",
        f"- Carry proxy: {_fmt_bps(e.get('carry_proxy'))}",
        f"- Total costs: {_fmt_bps(e.get('total_cost'))}",
        f"- Net return: {_fmt_bps(e.get('net_return'))}",
        f"- Edge ratio: {_fmt_ratio(e.get('edge_ratio'))}",
        f"- Required minimum edge: {_fmt_bps(e.get('required_minimum_edge'))}",
        "",
        "TRANSACTION COSTS:",
        f"- Spread: {_fmt_bps(c.get('spread'))}",
        f"- Slippage: {_fmt_bps(c.get('slippage'))}",
        f"- Commission: {_fmt_bps(c.get('commission'))}",
        f"- VIX: {c.get('vix', '—')}",
        "",
        "MODEL SIGNAL:",
        f"- Probability up: {a.get('probability_up', 0) * 100:.4f}%",
        f"- Expected return: {_fmt_bps(a.get('expected_return'))}",
        f"- Expected volatility: {a.get('expected_volatility', 0) * 100:.2f}%",
        f"- Model: {a.get('model_id', '—')} {a.get('model_version', '')}",
        "",
        "SIGNAL COMPONENTS:",
        f"- Quant score: {_score(s, 'quant_score')}",
        f"- Macro score: {_score(s, 'macro_score')}",
        f"- RAG score: {_score(s, 'rag_score')}",
        "",
        "QUALITY:",
        f"- Score: {q.get('score', '—')}",
        f"- Level: {q.get('level', '—')}",
        f"- Confidence: {(q.get('components') or {}).get('confidence', '—')}",
        f"- Freshness: {(q.get('components') or {}).get('freshness', '—')}",
        f"- Regime alignment: {(q.get('components') or {}).get('regime_alignment', '—')}",
        "",
        "RISK:",
        f"- Score: {r.get('risk_score', '—')}",
        f"- Level: {r.get('risk_level', '—')}",
        "",
        "GATES:",
        f"- All passed: {'YES' if g.get('all_passed') else 'NO'}",
        f"- First failing: {g.get('first_failing_gate') or 'none'}",
        f"- Degraded warnings: {g.get('degraded_warnings') or []}",
        "",
        "MACRO CONTEXT:",
        f"- Status: {m.get('status', '—')}",
        f"- Base rate: {m.get('base_rate', '—')}",
        f"- Quote rate: {m.get('quote_rate', '—')}",
        f"- Policy differential: {m.get('policy_differential', '—')}",
        f"- Growth differential: {m.get('growth_differential', '—')}",
        f"- Inflation differential: {m.get('inflation_differential', '—')}",
        "",
        "TASK:",
        "Write 2-3 paragraphs in plain English explaining:",
        "1. What the system decided and why it matters.",
        "2. What the signal validity status means (VALID / DEGRADED / INVALID).",
        "3. How confident the user should be given the data quality.",
        "",
        "Explain any technical term you use. Keep it clear and factual.",
    ]
    return "\n".join(lines)


def build_fallback_narrative(decision_result: Dict[str, Any]) -> str:
    """
    Deterministic fallback when the LLM is unavailable.
    """
    d = decision_result.get("decision") or {}
    e = decision_result.get("economic") or {}
    g = decision_result.get("gate") or {}
    m = decision_result.get("macro_data_status") or {}

    pair = d.get("pair", "the pair")
    direction = d.get("direction", "NEUTRAL")
    confidence = d.get("confidence", 0.0)
    actionable = d.get("actionable", False)
    validity = d.get("signal_validity", "UNKNOWN")

    p1 = (
        f"The system identifies a {direction} signal for {pair} with "
        f"{confidence * 100:.1f}% confidence. "
        f"The signal is {'classified as actionable' if actionable else 'not classified as actionable'}, "
        f"and its validity status is {validity}."
    )

    p2 = ""
    if e:
        p2 = (
            f"After accounting for transaction costs, the expected net return "
            f"is {e.get('net_return', 0):.2f} basis points, producing an edge "
            f"ratio of {e.get('edge_ratio', 0):.2f}× against the required "
            f"threshold of {e.get('required_minimum_edge', 0):.1f} basis points."
        )

    p3 = ""
    warnings = (g.get("degraded_warnings") or [])
    if warnings:
        p3 = (
            f"The signal is marked as {validity} because: {'; '.join(warnings)}. "
            f"Macro status is {m.get('status', 'UNKNOWN')}. "
            f"Users should interpret this decision with appropriate caution."
        )
    elif validity == "VALID":
        p3 = (
            "All hard gates passed and no degraded warnings were raised. "
            "The signal is considered valid under the current data conditions."
        )

    parts = [p for p in [p1, p2, p3] if p]
    return "\n\n".join(parts)
