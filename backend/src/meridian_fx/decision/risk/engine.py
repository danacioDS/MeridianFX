"""Layer 2 v2.3.0 — Risk Engine.

Computes a RiskAssessment from pipeline inputs.

The engine does NOT know or modify Decision.
It receives raw inputs and returns an isolated RiskAssessment.

Methodology (frozen):
    risk_score =
        100 × (
            0.30 × volatility
          + 0.25 × macro
          + 0.20 × model
          + 0.15 × regime
          + 0.10 × edge
        )

Normalizations:
    volatility = clip((VIX - 10) / (30 - 10), 0, 1)
    macro       = FULL → 0.0 | PARTIAL → 0.5 | UNAVAILABLE → 1.0
    model       = 1 - confidence
    regime      = UNKNOWN → 1.0 | known → 0.0
    edge        = clip(1 - (edge_ratio / 5.0), 0, 1)
"""

from __future__ import annotations

from .models import (
    METHODOLOGY_VERSION,
    RiskAssessment,
    RiskDriver,
    RiskLevel,
)

# Weights (frozen for v2.3.0)
W_VOLATILITY = 0.30
W_MACRO = 0.25
W_MODEL = 0.20
W_REGIME = 0.15
W_EDGE = 0.10

# Volatility normalization
VIX_FLOOR = 10.0
VIX_CEIL = 30.0

# Edge normalization
EDGE_CEIL = 5.0

# Risk level thresholds
LOW_THRESHOLD = 25.0
MODERATE_THRESHOLD = 50.0
HIGH_THRESHOLD = 75.0


class RiskEngine:
    """Computes RiskAssessment without touching Decision."""

    def compute(
        self,
        vix: float | None,
        macro_status: str,
        confidence: float,
        regime: str,
        edge_ratio: float,
    ) -> RiskAssessment:
        drivers: list[RiskDriver] = []

        # 1. Volatility
        vol_norm = self._normalize_volatility(vix)
        drivers.append(
            RiskDriver(
                name="volatility",
                contribution=round(W_VOLATILITY * vol_norm * 100.0, 6),
                normalized_value=round(vol_norm, 6),
                weight=W_VOLATILITY,
                explanation=(
                    f"VIX {vix:.1f} → normalized {vol_norm:.2f}"
                    if vix is not None
                    else "VIX unavailable"
                ),
            )
        )

        # 2. Macro uncertainty
        macro_norm = self._normalize_macro(macro_status)
        drivers.append(
            RiskDriver(
                name="macro",
                contribution=round(W_MACRO * macro_norm * 100.0, 6),
                normalized_value=round(macro_norm, 6),
                weight=W_MACRO,
                explanation=f"Macro status: {macro_status}",
            )
        )

        # 3. Model uncertainty
        model_norm = self._normalize_model(confidence)
        drivers.append(
            RiskDriver(
                name="model",
                contribution=round(W_MODEL * model_norm * 100.0, 6),
                normalized_value=round(model_norm, 6),
                weight=W_MODEL,
                explanation=f"Model confidence: {confidence:.2f}",
            )
        )

        # 4. Regime uncertainty
        regime_norm = self._normalize_regime(regime)
        drivers.append(
            RiskDriver(
                name="regime",
                contribution=round(W_REGIME * regime_norm * 100.0, 6),
                normalized_value=round(regime_norm, 6),
                weight=W_REGIME,
                explanation=f"Regime: {regime}",
            )
        )

        # 5. Edge quality
        edge_norm = self._normalize_edge(edge_ratio)
        drivers.append(
            RiskDriver(
                name="edge",
                contribution=round(W_EDGE * edge_norm * 100.0, 6),
                normalized_value=round(edge_norm, 6),
                weight=W_EDGE,
                explanation=f"Edge ratio: {edge_ratio:.2f}",
            )
        )

        risk_score = round(sum(d.contribution for d in drivers), 6)
        risk_level = self._level_for(risk_score)

        return RiskAssessment(
            risk_score=risk_score,
            risk_level=risk_level,
            drivers=drivers,
            methodology_version=METHODOLOGY_VERSION,
        )

    # ------------------------------------------------------------------
    # Normalizations
    # ------------------------------------------------------------------
    @staticmethod
    def _normalize_volatility(vix: float | None) -> float:
        if vix is None:
            return 1.0  # highest uncertainty
        norm = (vix - VIX_FLOOR) / (VIX_CEIL - VIX_FLOOR)
        return max(0.0, min(1.0, norm))

    @staticmethod
    def _normalize_macro(status: str) -> float:
        s = (status or "").upper()
        if s == "FULL":
            return 0.0
        if s == "PARTIAL":
            return 0.5
        return 1.0  # UNAVAILABLE or unknown

    @staticmethod
    def _normalize_model(confidence: float) -> float:
        c = max(0.0, min(1.0, confidence))
        return 1.0 - c

    @staticmethod
    def _normalize_regime(regime: str) -> float:
        r = (regime or "").upper()
        if r == "UNKNOWN" or r == "":
            return 1.0
        return 0.0

    @staticmethod
    def _normalize_edge(edge_ratio: float) -> float:
        norm = 1.0 - (edge_ratio / EDGE_CEIL)
        return max(0.0, min(1.0, norm))

    @staticmethod
    def _level_for(score: float) -> RiskLevel:
        if score < LOW_THRESHOLD:
            return RiskLevel.LOW
        if score < MODERATE_THRESHOLD:
            return RiskLevel.MODERATE
        if score < HIGH_THRESHOLD:
            return RiskLevel.HIGH
        return RiskLevel.EXTREME
