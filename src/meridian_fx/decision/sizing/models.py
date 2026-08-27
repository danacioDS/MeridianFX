"""Layer 2 v3.4.1 §11 — Position sizing models (unchanged).

Position block (DecisionRecord §13):
    position_size
    base_size
    available_capacity
    multipliers: { edge, quality, volatility }
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from ..contracts.decision import RejectionReason


class PositionMultipliers(BaseModel):
    """Multipliers, all bounded per §11 caps: edge [0, 2.0], quality [0, 1.0],
    volatility [0.25, 1.25]."""

    model_config = ConfigDict(extra="forbid")

    edge: float = Field(ge=0.0, le=2.0)
    quality: float = Field(ge=0.0, le=1.0)
    volatility: float = Field(ge=0.25, le=1.25)


class PositionSizeResult(BaseModel):
    """Output of PositionSizingEngine.calculate (L2 §11)."""

    model_config = ConfigDict(extra="forbid")

    position_size: float
    base_size: float
    available_capacity: float
    multipliers: PositionMultipliers
    rejection_reason: RejectionReason | None = None
    capacity_constrained: bool = False