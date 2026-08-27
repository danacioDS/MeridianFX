"""Layer 2 v3.4.1 §7.1 — Economic filter (no formula changes).

All units in BASIS POINTS (bps).

    directional_gross_return = expected_return x direction_sign
                              (expected_return ALWAYS LONG/base-quote)
    carry_proxy = direction_sign x (base_rate - quote_rate)
                  x horizon_days / 365 x 10000        # PROXY, not actual carry
    net_return = directional_gross_return + carry_proxy - total_cost
    edge_ratio = net_return / required_minimum_edge
    actionable = edge_ratio >= 1.0

    required_minimum_edge MUST be > 0.
    IF required_minimum_edge <= 0 → INVALID, rejection = INVALID_EDGE_THRESHOLD
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from ..contracts.decision import RejectionReason
from ..contracts.fusion import DIRECTION_SIGN, Direction


class EdgeThresholdInvalidError(RuntimeError):
    """required_minimum_edge <= 0 → INVALID (not UNAVAILABLE)."""

    reason = RejectionReason.INVALID_EDGE_THRESHOLD


class EconomicFilterResult(BaseModel):
    """Outputs of §7.1 (mirrors DecisionRecord.economic_filter)."""

    model_config = ConfigDict(extra="forbid")

    directional_gross_return: float  # bps
    carry_proxy: float  # bps (proxy, not actual carry)
    total_cost: float  # bps
    net_return: float  # bps
    edge_ratio: float
    required_minimum_edge: float
    actionable: bool


class EconomicFilter:
    """Computes net return, edge ratio and actionability (L2 §7.1)."""

    def apply(
        self,
        expected_return: float,
        direction: Direction,
        base_rate: float,
        quote_rate: float,
        horizon_days: int,
        total_cost: float,
        required_minimum_edge: float,
    ) -> EconomicFilterResult:
        if required_minimum_edge <= 0:
            raise EdgeThresholdInvalidError(
                "required_minimum_edge must be > 0 → INVALID"
            )
        sign = DIRECTION_SIGN[direction]

        directional_gross_return = expected_return * sign
        carry_proxy = (
            sign * (base_rate - quote_rate) * horizon_days / 365.0 * 10000.0
        )
        net_return = directional_gross_return + carry_proxy - total_cost
        edge_ratio = net_return / required_minimum_edge

        return EconomicFilterResult(
            directional_gross_return=round(directional_gross_return, 6),
            carry_proxy=round(carry_proxy, 6),
            total_cost=round(total_cost, 6),
            net_return=round(net_return, 6),
            edge_ratio=round(edge_ratio, 6),
            required_minimum_edge=round(required_minimum_edge, 6),
            actionable=edge_ratio >= 1.0,
        )