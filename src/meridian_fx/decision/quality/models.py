"""Layer 2 v3.4.1 §9 — Decision quality models (no structural changes).

DecisionQuality:
    decision_quality = 0.30 x confidence
                     + 0.25 x freshness
                     + 0.20 x regime_alignment
                     + 0.15 x data_quality
                     + 0.10 x drift_score

    freshness = exp(-age_hours / 24)
    drift_score = 1 - min(1, PSI / 0.20)  (PSI missing → 0.50, status FALLBACK)



QUALITY LEVELS:
    >= 0.70: HIGH | 0.50-0.70: MODERATE | < 0.50: LOW

Patch P6: data_quality_status maps to DecisionQuality.components.data_quality:
    good >= 0.80, acceptable 0.60-0.80, degraded < 0.60.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class QualityLevel(StrEnum):
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"


class FallbackStatus(BaseModel):
    """Auditability of imputed components (§9 / DecisionRecord §13)."""

    model_config = ConfigDict(extra="forbid")

    drift: Literal["VALID", "FALLBACK"] = "VALID"
    normalization: Literal["VALID", "FALLBACK"] = "VALID"
    diversification: Literal["VALID", "FALLBACK"] = "VALID"


class DecisionQualityComponents(BaseModel):
    """Quality components (all in [0, 1]).

    Patch P6: ``data_quality`` holds the STATUS ("good" | "acceptable" |
    "degraded") derived from the numeric ``data_quality_score`` kept in the
    parallel numeric field used by the §9 formula.
    """

    model_config = ConfigDict(extra="forbid")

    confidence: float = Field(ge=0.0, le=1.0)
    freshness: float = Field(ge=0.0, le=1.0)
    regime_alignment: float = Field(ge=0.0, le=1.0)
    data_quality: str  # Patch P6 — "good" | "acceptable" | "degraded"
    data_quality_score: float = Field(ge=0.0, le=1.0)
    drift_score: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def _status_consistent(self) -> "DecisionQualityComponents":
        """Map numeric score → status per Patch P6 (>=0.80 good, 0.60-0.80
        acceptable, <0.60 degraded)."""
        score = self.data_quality_score
        expected = "good" if score >= 0.80 else "acceptable" if score >= 0.60 else "degraded"
        if expected != self.data_quality:
            raise ValueError(
                f"data_quality_status {self.data_quality!r} inconsistent with "
                f"score {score} (Patch P6 expects {expected!r})"
            )
        return self


class DecisionQuality(BaseModel):
    """§9 decision-quality result (mirrors DecisionRecord.decision_quality)."""

    model_config = ConfigDict(extra="forbid")

    score: float = Field(ge=0.0, le=1.0)
    components: DecisionQualityComponents
    level: QualityLevel
    fallback_status: FallbackStatus = Field(default_factory=FallbackStatus)