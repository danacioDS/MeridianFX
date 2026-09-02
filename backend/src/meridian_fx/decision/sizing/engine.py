"""Layer 2 v3.4.1 §11 — Position sizing engine (NO CIRCULARITY).

    IF actionable == false OR any hard gate fails:
        position_size = 0
    ELSE:
        pre = base_size x edge_multiplier x quality_multiplier x volatility_multiplier
        available_capacity = max_exposure - current_exposure
        IF available_capacity <= 0:
            position_size = 0, rejection = CONCENTRATION_LIMIT
        ELSE:
            position_size = min(pre, available_capacity)

    multipliers: edge = min(edge_ratio, 2.0)
                 quality = decision_quality
                 volatility = clip(20 / (VIX + 10), 0.25, 1.25)

Patch P7 (prompt v1.1):
  * The capacity check is a SECONDARY SAFETY mechanism.
  * It does NOT modify the GateResult from HardGateEngine.
  * Gate #3 (Concentration) determines ELIGIBILITY; position sizing applies
    AVAILABLE CAPACITY. These are DISTINCT concerns.
"""

from __future__ import annotations

from ..contracts.decision import RejectionReason
from .models import PositionMultipliers, PositionSizeResult

MAX_EDGE_MULTIPLIER = 2.0
VOLATILITY_MIN = 0.25
VOLATILITY_MAX = 1.25
VOLATILITY_COMPONENT_WEIGHT = 20.0


class PositionSizingEngine:
    """Computes position size without circularity (L2 §11)."""

    def calculate(
        self,
        actionable: bool,
        all_gates_passed: bool,
        rejection_reason: RejectionReason | None,
        base_size: float,
        edge_ratio: float,
        decision_quality: float,
        vix: float | None,
        current_exposure: float,
        max_exposure: float,
    ) -> PositionSizeResult:
        if vix is None:
            # VIX is a Layer 4 precondition (Patch P2); never invent a value.
            return self._zero(
                base_size=base_size,
                current_exposure=current_exposure,
                max_exposure=max_exposure,
                reason=RejectionReason.VIX_UNAVAILABLE,
            )

        multipliers = PositionMultipliers(
            edge=max(0.0, min(edge_ratio, MAX_EDGE_MULTIPLIER)),
            quality=max(0.0, min(1.0, decision_quality)),
            volatility=max(
                VOLATILITY_MIN,
                min(VOLATILITY_MAX, VOLATILITY_COMPONENT_WEIGHT / (vix + 10.0)),
            ),
        )

        if (not actionable) or (not all_gates_passed):
            # §11 R2: no trade — position is zero, reason carried from gates.
            return self._zero(
                base_size=base_size,
                current_exposure=current_exposure,
                max_exposure=max_exposure,
                reason=rejection_reason or RejectionReason.INSUFFICIENT_EDGE,
            )

        pre_concentration_position = (
            base_size * multipliers.edge * multipliers.quality * multipliers.volatility
        )
        available_capacity = max_exposure - current_exposure

        if available_capacity <= 0:
            return self._zero(
                base_size=base_size,
                current_exposure=current_exposure,
                max_exposure=max_exposure,
                reason=RejectionReason.CONCENTRATION_LIMIT,
                multipliers=multipliers,
            )

        position_size = min(pre_concentration_position, available_capacity)
        return PositionSizeResult(
            position_size=round(position_size, 6),
            base_size=base_size,
            available_capacity=round(available_capacity, 6),
            multipliers=multipliers,
            rejection_reason=None,
            capacity_constrained=position_size < pre_concentration_position,
        )

    @staticmethod
    def _zero(
        base_size: float,
        current_exposure: float,
        max_exposure: float,
        reason: RejectionReason,
        multipliers: PositionMultipliers | None = None,
    ) -> PositionSizeResult:
        return PositionSizeResult(
            position_size=0.0,
            base_size=base_size,
            available_capacity=round(max_exposure - current_exposure, 6),
            multipliers=multipliers
            or PositionMultipliers(edge=0.0, quality=0.0, volatility=VOLATILITY_MIN),
            rejection_reason=reason,
            capacity_constrained=False,
        )