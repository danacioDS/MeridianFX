"""Layer 2 v3.4.1 §13 / Prompt 1 — Decision domain contract.

Frozen interface (Prompt 1, patches P1, P3, P8):

    Decision = {
        decision_id: str
        prediction_id: str          # MUST reference a complete PredictionArtifact (P1)
        pair: str
        timestamp: datetime (UTC)
        as_of: datetime (UTC)
        horizon_days: int
        actionable: bool
        direction: "LONG" | "SHORT" | "NEUTRAL"
        confidence: float           # [0, 1]
        edge_ratio: float
        net_return: float           # bps
        position_size: float
        rejection_reason: str | None
        signal_validity: "VALID" | "DEGRADED" | "INVALID" | "UNAVAILABLE"
        created_at: datetime (UTC)
    }

Governance:
  * DO NOT add fields belonging to L1 (delivery_state, delivery_reason) or L3.
  * signal_validity is assigned DIRECTLY from GateResult (P3).
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .fusion import Direction
from .time import ensure_utc, utcnow


class SignalValidity(StrEnum):
    VALID = "VALID"
    DEGRADED = "DEGRADED"
    INVALID = "INVALID"
    UNAVAILABLE = "UNAVAILABLE"

    @classmethod
    def has_value(cls, value: str) -> bool:
        try:
            cls(value)
            return True
        except ValueError:
            return False


class RejectionReason(StrEnum):
    """Canonical rejection reasons — Layer 2 v3.4.1 §14 R4."""

    INSUFFICIENT_EDGE = "INSUFFICIENT_EDGE"
    DATA_QUALITY_DEGRADED = "DATA_QUALITY_DEGRADED"
    PIT_VIOLATION = "PIT_VIOLATION"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    REGIME_MISALIGNMENT = "REGIME_MISALIGNMENT"
    CONCENTRATION_LIMIT = "CONCENTRATION_LIMIT"
    CORRELATION_FILTER = "CORRELATION_FILTER"
    INVALID_EDGE_THRESHOLD = "INVALID_EDGE_THRESHOLD"
    VIX_UNAVAILABLE = "VIX_UNAVAILABLE"
    # Component score outside [-1, +1] without normalization (§12 INVALID).
    SIGNAL_OUT_OF_BOUNDS = "SIGNAL_OUT_OF_BOUNDS"


class Decision(BaseModel):
    """The Layer 2 decision contract (Prompt 1, frozen)."""

    model_config = ConfigDict(extra="forbid")

    decision_id: str
    prediction_id: str  # MUST reference a complete PredictionArtifact (P1)
    pair: str
    timestamp: datetime = Field(...)
    as_of: datetime = Field(...)
    horizon_days: int
    actionable: bool
    direction: Direction
    confidence: float = Field(ge=0.0, le=1.0)
    edge_ratio: float
    net_return: float  # bps
    position_size: float
    rejection_reason: RejectionReason | None = None
    signal_validity: SignalValidity
    created_at: datetime = Field(default_factory=utcnow)

    # Temporal invariants (PIT-5): all timestamps timezone-aware UTC.
    _tz_checked = field_validator("timestamp", "as_of", "created_at")(ensure_utc)

    # Patch P8: DO NOT add delivery_state / delivery_reason here.
    # Those are Layer 1 concern (delivery policy). Model allows no extra fields.


class DecisionContext(BaseModel):
    """Snapshot of all inputs evaluated by the Layer 2 pipeline.

    This is the object passed to HardGateEngine.evaluate() (Prompt 6).
    Field documentation follows Layer 2 v3.4.1 §8 / §12.
    """

    model_config = ConfigDict(extra="forbid")

    pair: str
    prediction_timestamp: datetime
    as_of: datetime
    horizon_days: int = Field(ge=1)

    # Gate #1 — UNAVAILABLE
    model_loaded: bool = True
    required_data_missing: bool = False
    vix: float | None = None  # ONLY from Layer 4 FeatureStore.get_feature('vix', T) (P2)

    # Gate #2 — INVALID
    quant_score: float | None = None
    macro_score: float | None = None
    rag_score: float | None = None
    required_minimum_edge: float = 0.0
    derived_available_time: datetime | None = None
    input_available_times: list[datetime] = Field(default_factory=list)

    # Gate #3 — CONCENTRATION (pre-capacity, §8)
    current_exposure: float = 0.0
    max_exposure: float = 1.0

    # Gate #4 — DATA QUALITY (threshold 0.60)
    data_quality_score: float | None = None
    data_quality_status: str | None = None

    # Gate #5 — ECONOMIC FILTER (edge_ratio threshold 1.0)
    expected_return: float = 0.0
    base_rate: float = 0.0
    quote_rate: float = 0.0
    direction: Direction = Direction.NEUTRAL
    total_cost: float | None = None
    edge_ratio: float | None = None
    net_return: float | None = None

    # Gate #6 — CORRELATION (threshold 0.70)
    max_abs_correlation: float | None = None

    # Gate #7 — REGIME MISALIGNMENT (threshold 0.30)
    regime_alignment: float | None = None

    # Degraded-signal detection (§12), used only when all gates pass
    age_hours: float | None = None
    data_coverage_pct: float | None = None

    @field_validator("prediction_timestamp", "as_of", "derived_available_time")
    @classmethod
    def _tz_utc(cls, v: datetime | None) -> datetime | None:
        return ensure_utc(v)