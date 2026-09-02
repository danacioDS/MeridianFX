"""Layer 3 v5.0 §11.2 — PredictionArtifact (frozen cross-layer contract).

This module hosts the Layer 3 prediction contract CONSUMED by Layer 2.

Governance (Prompt 1 / Patch P1):
  * Decision.prediction_id MUST reference a complete PredictionArtifact.
  * DO NOT redefine PredictionArtifact — it is defined by Layer 3 v5.0 §11.2.
  * All PredictionArtifact fields are available for use by Layer 2.

Definitive interface: docs/Product_specification/Layer_03.md §11.2 (v5.0 FROZEN).
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .time import ensure_utc

#: Fields a Decision.prediction_id MUST be able to resolve (Patch P1).
REQUIRED_PREDICTION_FIELDS: tuple[str, ...] = (
    "probability_up",
    "expected_return",
    "expected_volatility",
    "confidence_interval",
    "shap_values",
    "macro_regime",
    "rag_signal_ids",
    "feature_snapshot_id",
    "dataset_id",
    "as_of",
    "model_id",
    "model_version",
)


class ConfidenceInterval(BaseModel):
    """Prediction interval {lower, upper} per L3 v5.0 §11.2."""

    model_config = ConfigDict(extra="forbid")

    lower: float
    upper: float

    @field_validator("upper")
    @classmethod
    def _upper_at_least_lower(cls, v: float, info) -> float:
        lower = info.data.get("lower")
        if lower is not None and v < lower:
            raise ValueError("confidence_interval.upper must be >= lower")
        return v

    @property
    def width(self) -> float:
        return self.upper - self.lower


class MacroRegime(BaseModel):
    """Macro regime context {risk, policy, growth, inflation} (L3 v5.0 §11.2)."""

    model_config = ConfigDict(extra="forbid")

    risk: str
    policy: str
    growth: str
    inflation: str


class ShapValue(BaseModel):
    """SHAP contribution {feature, value} (L3 v5.0 §11.2)."""

    model_config = ConfigDict(extra="forbid")

    feature: str
    value: float


class Reproducibility(BaseModel):
    """Reproducibility block (L3 v5.0 §11.2)."""

    model_config = ConfigDict(extra="forbid")

    git_commit: str
    docker_image: str
    mlflow_run_id: str


class PredictionArtifact(BaseModel):
    """Layer 3 prediction artifact — the complete input to Layer 2.

    Interface exactly per docs/Product_specification/Layer_03.md §11.2 (v5.0).
    Owned by Layer 3; Layer 2 only consumes it.
    """

    model_config = ConfigDict(extra="forbid")

    prediction_id: str
    model_id: str
    model_version: str
    pair: str
    prediction_timestamp: datetime
    horizon_days: int

    # Outputs
    probability_up: float = Field(ge=0.0, le=1.0)
    expected_return: float
    expected_volatility: float = Field(ge=0.0)
    confidence_interval: ConfidenceInterval

    # Context
    regime_id: str
    macro_regime: MacroRegime
    rag_signal_ids: list[str] = Field(default_factory=list)
    shap_values: list[ShapValue] = Field(default_factory=list)

    # Data
    feature_snapshot_id: str
    dataset_id: str
    feature_version: str
    as_of: datetime

    # Research gate
    research_gate_status: Literal["APPROVED", "REJECTED", "PENDING"] = "APPROVED"

    # Reproducibility
    reproducibility: Reproducibility | None = None

    created_at: datetime | None = None

    # Temporal invariants (PIT-5): all timestamps timezone-aware UTC.
    _tz_checked = field_validator(
        "prediction_timestamp", "as_of", "created_at"
    )(ensure_utc)