"""Layer 2 v3.4.1 §10 / Prompt 10 — Opportunity ranking registry.

RankedOpportunity mirrors Layer 1 v5.1 §7.3 ``RankedOpportunity``:

    rank, pair, direction, opportunity_score, edge_ratio, actionable,
    confidence, decision_quality, position_size, prediction_id, decision_id

Opportunity Score (L2 §10, DEFAULT WEIGHTS α=0.35, β=0.25, γ=0.25, δ=0.15):

    Opportunity_Score = α x normalized_signal_strength
                      + β x normalized_risk_adj_return
                      + γ x decision_quality
                      + δ x diversification_benefit

    normalized_signal_strength  = |fusion_score|                 [0, 1]
    normalized_risk_adj_return  = (x - P5)/(P95 - P5), clipped   [0, 1]
        IF P95 == P5 OR fewer than 30 observations → 0.5 (FALLBACK)
    diversification_benefit     = 1 - min(1, max_abs_correlation)
        IF no existing positions or correlation unavailable → 0.5 (FALLBACK)
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from ..contracts.fusion import Direction

DEFAULT_WEIGHTS = {"alpha": 0.35, "beta": 0.25, "gamma": 0.25, "delta": 0.15}
MIN_OBSERVATIONS = 30
CORRELATION_CEILING = 1.0


class RankedOpportunity(BaseModel):
    """Ranking output, consumed verbatim by Layer 1 v5.1 §7.3."""

    model_config = ConfigDict(extra="forbid")

    rank: int
    pair: str
    direction: Direction
    opportunity_score: float
    edge_ratio: float
    actionable: bool
    confidence: float
    decision_quality: float
    position_size: float
    prediction_id: str
    decision_id: str


class OpportunityScoreInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fusion_score: float = Field(ge=-1.0, le=1.0)
    risk_adj_return: float | None = None  # x to normalize over window
    decision_quality: float = Field(ge=0.0, le=1.0)
    max_abs_correlation: float | None = None
    window: list[float] = Field(default_factory=list)  # rolling 60-day window


class OpportunityScoreResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    opportunity_score: float
    normalized_signal_strength: float
    normalized_risk_adj_return: float
    decision_quality: float
    diversification_benefit: float
    normalization_status: Literal["VALID", "FALLBACK"]
    diversification_status: Literal["VALID", "FALLBACK"]


class OpportunityScorer:
    """Computes the §10 opportunity score."""

    @staticmethod
    def normalized_risk_adj_return(x: float | None, window: list[float]) -> tuple[float, str]:
        if x is None or len(window) < MIN_OBSERVATIONS:
            return 0.5, "FALLBACK"
        p5, p95 = min(window), max(window)  # empirical P5/P95 of the window
        if p95 == p5:
            return 0.5, "FALLBACK"
        normalized = (x - p5) / (p95 - p5)
        return max(0.0, min(1.0, normalized)), "VALID"

    @staticmethod
    def diversification_benefit(max_abs_correlation: float | None) -> tuple[float, str]:
        if max_abs_correlation is None:
            return 0.5, "FALLBACK"
        return max(0.0, min(1.0, 1.0 - min(CORRELATION_CEILING, abs(max_abs_correlation)))), "VALID"

    def score(
        self,
        inputs: OpportunityScoreInput,
        weights: dict[str, float] | None = None,
    ) -> OpportunityScoreResult:
        w = weights or DEFAULT_WEIGHTS
        signal_strength = abs(inputs.fusion_score)
        risk_adj, norm_status = self.normalized_risk_adj_return(
            inputs.risk_adj_return, inputs.window
        )
        div, div_status = self.diversification_benefit(inputs.max_abs_correlation)
        opportunity_score = (
            w["alpha"] * signal_strength
            + w["beta"] * risk_adj
            + w["gamma"] * inputs.decision_quality
            + w["delta"] * div
        )
        return OpportunityScoreResult(
            opportunity_score=round(max(0.0, min(1.0, opportunity_score)), 6),
            normalized_signal_strength=round(signal_strength, 6),
            normalized_risk_adj_return=round(risk_adj, 6),
            decision_quality=round(inputs.decision_quality, 6),
            diversification_benefit=round(div, 6),
            normalization_status=norm_status,
            diversification_status=div_status,
        )


class OpportunityRegistry:
    """Stores and ranks Layer 2 opportunities (L1 §7.3 consumption)."""

    def __init__(self) -> None:
        self._opportunities: list[RankedOpportunity] = []

    def register(self, opportunity: RankedOpportunity) -> str:
        self._opportunities.append(opportunity)
        self._opportunities.sort(key=lambda o: o.opportunity_score, reverse=True)
        for rank, opp in enumerate(self._opportunities, start=1):
            opp.rank = rank
        return opportunity.decision_id

    def get_ranking(self, limit: int = 100, as_of: datetime | None = None) -> list[RankedOpportunity]:
        return self._opportunities[:limit]

    def get_top(self) -> RankedOpportunity | None:
        return self._opportunities[0] if self._opportunities else None

    def total_actionable(self) -> int:
        return sum(1 for o in self._opportunities if o.actionable)

    def __len__(self) -> int:
        return len(self._opportunities)