"""Layer 2 v3.4.1 §4 & §8 — Regime context and alignment policy.

§4 Regime determination (scoring-based):
    +1.0 exact match, +0.5 partial match, +0.0 mismatch per dimension.
    best_regime = argmax(score); max_score >= 2.5 → regime else "UNKNOWN".

§8 Regime Alignment (EXACT FORMULA, policy version "1.0"):
    regime_alignment = 0.30 x global_alignment
                     + 0.35 x base_alignment
                     + 0.35 x quote_alignment

Alignment values are CONFIGURED POLICY PARAMETERS, not universal truths
(policy_version = "1.0"). Tables per L2 §8.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, field_validator

POLICY_VERSION = "1.0"


class Regime(StrEnum):
    EXPANSION = "Expansion"
    LATE_CYCLE = "Late Cycle"
    STAGFLATION = "Stagflation"
    RECOVERY = "Recovery"
    CRISIS = "Crisis"
    GOLDILOCKS = "Goldilocks"

    @classmethod
    def has_value(cls, value: str) -> bool:
        try:
            cls(value)
            return True
        except ValueError:
            return False


class GlobalRegime(StrEnum):
    RISK_ON = "Risk-On"
    NEUTRAL = "Neutral"
    RISK_OFF = "Risk-Off"

    @classmethod
    def has_value(cls, value: str) -> bool:
        try:
            cls(value)
            return True
        except ValueError:
            return False


class PolicyRegime(StrEnum):
    RESTRICTIVE = "Restrictive"
    NEUTRAL = "Neutral"
    ACCOMMODATIVE = "Accommodative"

    @classmethod
    def has_value(cls, value: str) -> bool:
        try:
            cls(value)
            return True
        except ValueError:
            return False


# ---------------------------------------------------------------------------
# §8 Alignment tables (configured policy parameters, version 1.0)
# ---------------------------------------------------------------------------

DIRECTIONS = ("LONG", "SHORT", "NEUTRAL")

GLOBAL_ALIGNMENT_TABLE: dict[str, dict[str, float]] = {
    GlobalRegime.RISK_ON: {"LONG": 1.00, "SHORT": 0.30, "NEUTRAL": 0.50},
    GlobalRegime.NEUTRAL: {"LONG": 0.75, "SHORT": 0.75, "NEUTRAL": 1.00},
    GlobalRegime.RISK_OFF: {"LONG": 0.30, "SHORT": 1.00, "NEUTRAL": 0.50},
}

#: base_alignment and quote_alignment share the same table (L2 §8).
BASE_QUOTE_ALIGNMENT_TABLE: dict[str, dict[str, float]] = {
    PolicyRegime.RESTRICTIVE: {"LONG": 0.80, "SHORT": 0.40, "NEUTRAL": 0.50},
    PolicyRegime.NEUTRAL: {"LONG": 0.75, "SHORT": 0.75, "NEUTRAL": 1.00},
    PolicyRegime.ACCOMMODATIVE: {"LONG": 0.40, "SHORT": 0.80, "NEUTRAL": 0.50},
}

#: Predefined regime profiles for §4 scoring-based determination.
#: Dimensions: risk, policy, growth, inflation.
REGIME_PROFILES: dict[str, dict[str, str]] = {
    Regime.GOLDILOCKS: {
        "risk": "Risk-On",
        "policy": "Neutral",
        "growth": "High",
        "inflation": "Low",
    },
    Regime.EXPANSION: {
        "risk": "Risk-On",
        "policy": "Accommodative",
        "growth": "High",
        "inflation": "Moderate",
    },
    Regime.LATE_CYCLE: {
        "risk": "Neutral",
        "policy": "Restrictive",
        "growth": "Moderate",
        "inflation": "Moderate",
    },
    Regime.STAGFLATION: {
        "risk": "Risk-Off",
        "policy": "Restrictive",
        "growth": "Low",
        "inflation": "High",
    },
    Regime.CRISIS: {
        "risk": "Risk-Off",
        "policy": "Accommodative",
        "growth": "Low",
        "inflation": "High",
    },
    Regime.RECOVERY: {
        "risk": "Neutral",
        "policy": "Accommodative",
        "growth": "Moderate",
        "inflation": "Low",
    },
}


class RegimeAlignmentInput(BaseModel):
    """Inputs to the §8 regime-alignment formula."""

    model_config = ConfigDict(extra="forbid")

    global_regime: str
    base_policy: str
    quote_policy: str
    direction: str  # "LONG" | "SHORT" | "NEUTRAL"

    @field_validator("direction")
    @classmethod
    def _direction_valid(cls, v: str) -> str:
        if v not in DIRECTIONS:
            raise ValueError(f"direction must be one of {DIRECTIONS}")
        return v

    @field_validator("global_regime")
    @classmethod
    def _global_valid(cls, v: str) -> str:
        if not GlobalRegime.has_value(v):
            raise ValueError(f"unknown global regime: {v}")
        return v

    @field_validator("base_policy", "quote_policy")
    @classmethod
    def _policy_valid(cls, v: str) -> str:
        if not PolicyRegime.has_value(v):
            raise ValueError(f"unknown policy regime: {v}")
        return v


def compute_regime_alignment(
    global_regime: str,
    base_policy: str,
    quote_policy: str,
    direction: str,
) -> float:
    """regime_alignment = 0.30 g + 0.35 b + 0.35 q  (L2 §8, policy v1.0)."""
    inputs = RegimeAlignmentInput(
        global_regime=global_regime,
        base_policy=base_policy,
        quote_policy=quote_policy,
        direction=direction,
    )
    g = GLOBAL_ALIGNMENT_TABLE[inputs.global_regime][inputs.direction]
    b = BASE_QUOTE_ALIGNMENT_TABLE[inputs.base_policy][inputs.direction]
    q = BASE_QUOTE_ALIGNMENT_TABLE[inputs.quote_policy][inputs.direction]
    alignment = 0.30 * g + 0.35 * b + 0.35 * q
    return round(min(1.0, max(0.0, alignment)), 6)


# Adjacent risk attitudes produce a PARTIAL (0.5) match (§4).
_RISK_PARTIAL_PAIRS = {("Risk-On", "Neutral"), ("Neutral", "Risk-Off")}


def _dimension_score(actual: str, expected: str) -> float:
    if actual == expected:
        return 1.0
    if (actual, expected) in _RISK_PARTIAL_PAIRS or (
        expected,
        actual,
    ) in _RISK_PARTIAL_PAIRS:
        return 0.5
    return 0.0


def determine_regime(macro_regime: dict[str, str]) -> str:
    """Scoring-based regime determination (L2 §4).

    Returns a Regime value or "UNKNOWN" when no profile reaches 2.5.
    """
    if not macro_regime:
        return "UNKNOWN"
    best_regime: str | None = None
    best_score = 0.0
    for regime, profile in REGIME_PROFILES.items():
        score = sum(_dimension_score(macro_regime.get(dim, ""), expected) for dim, expected in profile.items())
        if score > best_score:
            best_score = score
            best_regime = regime
    if best_regime is not None and best_score >= 2.5:
        return best_regime
    return "UNKNOWN"