"""Layer 2 v2.3.0 — Risk Assessment contracts.

RiskAssessment is SEPARATE from Decision:
- Decision: what to do (direction, edge, sizing)
- RiskAssessment: how risky is the thesis and why
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

METHODOLOGY_VERSION = "v2.3.0"


class RiskLevel(StrEnum):
    """Risk level classification (0-100 scale)."""

    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


class RiskDriver(BaseModel):
    """A single risk driver contributing to the risk_score."""

    model_config = ConfigDict(extra="forbid")

    name: str
    contribution: float = Field(ge=0.0, le=100.0)
    normalized_value: float = Field(ge=0.0, le=1.0)
    weight: float = Field(gt=0.0, le=1.0)
    explanation: str


class RiskAssessment(BaseModel):
    """Risk assessment for a decision thesis.

    risk_score=0 means minimum risk within the model (not risk-free).
    """

    model_config = ConfigDict(extra="forbid")

    risk_score: float = Field(ge=0.0, le=100.0)
    risk_level: RiskLevel
    drivers: list[RiskDriver] = Field(default_factory=list)
    methodology_version: str = METHODOLOGY_VERSION
