"""Layer 2 v3.4.1 §3 — Signal Generation (domain contracts).

Formula (unchanged):
    quant_score = 2 x (probability_up - 0.5)                         [-1, +1]
    macro_score = 0.50 x policy_differential
                + 0.25 x growth_differential
                + 0.25 x normalized_rate_differential                [-1, +1]
    rag_score   = (base_signal - quote_signal) x 0.5                 [-1, +1]

Invariant: every component score MUST be bounded to [-1, +1].
A value outside the band → INVALID (Gate #2, see §12).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

LOWER_BOUND = -1.0
UPPER_BOUND = 1.0


def raw_quant_score(probability_up: float) -> float:
    """Unvalidated §3 quant formula (pipeline uses it to detect OOB → INVALID)."""
    if not (0.0 <= probability_up <= 1.0):
        raise ValueError("probability_up must be within [0, 1]")
    return 2.0 * (probability_up - 0.5)


def raw_macro_score(
    policy_differential: float,
    growth_differential: float,
    normalized_rate_differential: float,
) -> float:
    """Unvalidated §3 macro formula."""
    return (
        0.50 * policy_differential
        + 0.25 * growth_differential
        + 0.25 * normalized_rate_differential
    )


def raw_rag_score(base_signal: float, quote_signal: float) -> float:
    """Unvalidated §3 rag formula."""
    return (base_signal - quote_signal) * 0.5


class SignalOutOfBoundsError(ValueError):
    """Raised when a component score escapes [-1, +1] (→ Gate #2 INVALID)."""


class ScoreComponent(BaseModel):
    """A single bounded [-1, +1] component score."""

    model_config = ConfigDict(extra="forbid")

    value: float

    @field_validator("value")
    @classmethod
    def _enforce_bounds(cls, v: float) -> float:
        if not (LOWER_BOUND <= v <= UPPER_BOUND):
            raise SignalOutOfBoundsError(
                f"component score {v} outside [-1, +1] → INVALID"
            )
        return v


class SignalComponents(BaseModel):
    """The three fused component scores (all bounded to [-1, +1])."""

    model_config = ConfigDict(extra="forbid")

    quant_score: ScoreComponent | float | None = None
    macro_score: ScoreComponent | float | None = None
    rag_score: ScoreComponent | float | None = None

    @field_validator("quant_score", "macro_score", "rag_score", mode="before")
    @classmethod
    def _coerce_score(cls, v) -> ScoreComponent | float | None:
        if v is None or isinstance(v, ScoreComponent):
            return v
        return ScoreComponent(value=v)


class SignalGenerator:
    """Deterministic generator of the three L2 §3 component scores."""

    @staticmethod
    def quant_score(probability_up: float) -> float:
        """quant_score = 2 x (probability_up - 0.5), probability_up in [0, 1]."""
        if not (0.0 <= probability_up <= 1.0):
            raise ValueError("probability_up must be within [0, 1]")
        return ScoreComponent(value=raw_quant_score(probability_up)).value

    @staticmethod
    def macro_score(
        policy_differential: float,
        growth_differential: float,
        normalized_rate_differential: float,
    ) -> float:
        """macro_score = 0.50p + 0.25g + 0.25r (L2 §3)."""
        score = raw_macro_score(
            policy_differential, growth_differential, normalized_rate_differential
        )
        if not (LOWER_BOUND <= score <= UPPER_BOUND):
            raise SignalOutOfBoundsError(
                f"macro_score {score} outside [-1, +1] → INVALID"
            )
        return score

    @staticmethod
    def rag_score(base_signal: float, quote_signal: float) -> float:
        """rag_score = (base_signal - quote_signal) x 0.5 (L2 §3)."""
        score = raw_rag_score(base_signal, quote_signal)
        if not (LOWER_BOUND <= score <= UPPER_BOUND):
            raise SignalOutOfBoundsError(
                f"rag_score {score} outside [-1, +1] → INVALID"
            )
        return score

    def generate(
        self,
        probability_up: float | None = None,
        policy_differential: float | None = None,
        growth_differential: float | None = None,
        normalized_rate_differential: float | None = None,
        base_signal: float | None = None,
        quote_signal: float | None = None,
        quant_score: float | None = None,
        macro_score: float | None = None,
        rag_score: float | None = None,
    ) -> SignalComponents:
        """Compose the three component scores.

        Pre-computed scores may be supplied directly (bypassing derivation);
        otherwise each is derived from its raw inputs.
        """
        components = SignalComponents(
            quant_score=quant_score,
            macro_score=macro_score,
            rag_score=rag_score,
        )
        derived = []
        if components.quant_score is None:
            if probability_up is None:
                raise ValueError("probability_up required to derive quant_score")
            derived.append(self.quant_score(probability_up))
        if components.macro_score is None:
            if None in (
                policy_differential,
                growth_differential,
                normalized_rate_differential,
            ):
                raise ValueError(
                    "macro differentials required to derive macro_score"
                )
            derived.append(
                self.macro_score(
                    policy_differential,
                    growth_differential,
                    normalized_rate_differential,
                )
            )
        if components.rag_score is None:
            if base_signal is None or quote_signal is None:
                raise ValueError("base/quote signals required to derive rag_score")
            derived.append(self.rag_score(base_signal, quote_signal))

        values = [
            components.quant_score.value if components.quant_score is not None else None,
            components.macro_score.value if components.macro_score is not None else None,
            components.rag_score.value if components.rag_score is not None else None,
        ]
        cursor = 0
        for i in range(3):
            if values[i] is None:
                values[i] = derived[cursor]
                cursor += 1
        return SignalComponents(
            quant_score=values[0], macro_score=values[1], rag_score=values[2]
        )