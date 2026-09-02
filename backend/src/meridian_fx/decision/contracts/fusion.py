"""Layer 2 v3.4.1 §5 & §6 — Dynamic Signal Fusion and Signal-Oriented Confidence.

§5 Fusion:
    fusion_score = wq(regime) x quant + wm(regime) x macro + wr(regime) x rag
    constraints: wq + wm + wr = 1.0, all >= 0.0

    NEUTRAL_THRESHOLD = 0.10 (strict inequality: ±0.10 → NEUTRAL)

§6 Confidence (signal-oriented):
    confidence = 0.40 x signal_strength + 0.30 x model_confidence
               + 0.20 x historical_reliability + 0.10 x cross_signal_agreement
    signal_strength = |fusion_score|
    cross_signal_agreement = 1 - (max - min) / 2

    model_confidence = 1 - normalized_interval_width
    normalized_interval_width = (width - P5) / (P95 - P5), clipped [0, 1]
    IF P95 == P5: normalized_interval_width = 0.5
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .regime import Regime
from .signal import SignalComponents

NEUTRAL_THRESHOLD = 0.10


class RegimeWeights(BaseModel):
    """Regime-dependent fusion weights (must sum to 1.0, all >= 0.0)."""

    model_config = ConfigDict(extra="forbid")

    quant: float = Field(ge=0.0)
    macro: float = Field(ge=0.0)
    rag: float = Field(ge=0.0)

    @field_validator("quant", "macro", "rag")
    @classmethod
    def _weights_permitted(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("weights must be within [0, 1]")
        return v

    def sum(self) -> float:
        return self.quant + self.macro + self.rag


FUSION_WEIGHTS: dict[str, RegimeWeights] = {
    Regime.EXPANSION: RegimeWeights(quant=0.50, macro=0.30, rag=0.20),
    Regime.LATE_CYCLE: RegimeWeights(quant=0.60, macro=0.25, rag=0.15),
    Regime.STAGFLATION: RegimeWeights(quant=0.40, macro=0.40, rag=0.20),
    Regime.RECOVERY: RegimeWeights(quant=0.40, macro=0.35, rag=0.25),
    Regime.CRISIS: RegimeWeights(quant=0.30, macro=0.40, rag=0.30),
    Regime.GOLDILOCKS: RegimeWeights(quant=0.55, macro=0.30, rag=0.15),
    "UNKNOWN": RegimeWeights(quant=0.50, macro=0.30, rag=0.20),
}


class Direction(StrEnum):
    LONG = "LONG"
    SHORT = "SHORT"
    NEUTRAL = "NEUTRAL"


DIRECTION_SIGN: dict[Direction, int] = {
    Direction.LONG: 1,
    Direction.SHORT: -1,
    Direction.NEUTRAL: 0,
}


class FusionResult(BaseModel):
    """Outputs of §5 fusion plus §6 signal-oriented confidence."""

    model_config = ConfigDict(extra="forbid")

    regime: str
    weights: RegimeWeights
    fusion_score: float
    direction: Direction
    direction_sign: int
    confidence: float | None = None


class FusionEngine:
    """§5 dynamic fusion with regime-dependent weights."""

    @staticmethod
    def weights_for(regime: str) -> RegimeWeights:
        try:
            weights = FUSION_WEIGHTS[regime]
        except KeyError as exc:
            raise ValueError(f"no fusion weights defined for regime {regime!r}") from exc
        total = weights.sum()
        if abs(total - 1.0) > 1e-9:
            raise ValueError("fusion weights must sum to 1.0")
        return weights

    def fuse(self, signals: SignalComponents, regime: str) -> FusionResult:
        weights = self.weights_for(regime)
        fusion_score = (
            weights.quant * signals.quant_score.value
            + weights.macro * signals.macro_score.value
            + weights.rag * signals.rag_score.value
        )
        fusion_score = round(min(1.0, max(-1.0, fusion_score)), 9)

        if fusion_score > NEUTRAL_THRESHOLD:
            direction = Direction.LONG
        elif fusion_score < -NEUTRAL_THRESHOLD:
            direction = Direction.SHORT
        else:
            direction = Direction.NEUTRAL

        return FusionResult(
            regime=regime,
            weights=weights,
            fusion_score=fusion_score,
            direction=direction,
            direction_sign=DIRECTION_SIGN[direction],
        )


class ConfidenceInput(BaseModel):
    """Raw inputs to the §6 confidence formula."""

    model_config = ConfigDict(extra="forbid")

    signal_strength: float = Field(ge=0.0, le=1.0)
    model_confidence: float = Field(ge=0.0, le=1.0)
    historical_reliability: float = Field(ge=0.0, le=1.0)
    cross_signal_agreement: float = Field(ge=0.0, le=1.0)


class ConfidenceResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    confidence: float
    components: ConfidenceInput


class ConfidenceCalculator:
    """§6 confidence = 0.40s + 0.30m + 0.20h + 0.10c."""

    W_SIGNAL = 0.40
    W_MODEL = 0.30
    W_HISTORICAL = 0.20
    W_CROSS = 0.10

    @staticmethod
    def signal_strength(fusion_score: float) -> float:
        return min(1.0, abs(fusion_score))

    @staticmethod
    def cross_signal_agreement(scores: list[float]) -> float:
        if not scores:
            return 0.5
        lo, hi = min(scores), max(scores)
        return 1.0 - (hi - lo) / 2.0

    @staticmethod
    def model_confidence_from_interval(
        width: float,
        p5_width: float = 0.0,
        p95_width: float = 1.0,
    ) -> float:
        """model_confidence = 1 - normalized_interval_width (§6)."""
        if p95_width == p5_width:
            normalized = 0.5
        else:
            normalized = (width - p5_width) / (p95_width - p5_width)
            normalized = max(0.0, min(1.0, normalized))
        return 1.0 - normalized

    def compute(
        self,
        fusion_score: float,
        quant_score: float,
        macro_score: float,
        rag_score: float,
        model_confidence: float,
        historical_reliability: float,
    ) -> ConfidenceResult:
        components = ConfidenceInput(
            signal_strength=self.signal_strength(fusion_score),
            model_confidence=model_confidence,
            historical_reliability=historical_reliability,
            cross_signal_agreement=self.cross_signal_agreement(
                [quant_score, macro_score, rag_score]
            ),
        )
        confidence = (
            self.W_SIGNAL * components.signal_strength
            + self.W_MODEL * components.model_confidence
            + self.W_HISTORICAL * components.historical_reliability
            + self.W_CROSS * components.cross_signal_agreement
        )
        return ConfidenceResult(confidence=round(min(1.0, max(0.0, confidence)), 6), components=components)