"""Layer 2 v3.4.1 §8/§12 — Hard gate engine (precedence + thresholds).

Each gate is evaluated against the DecisionContext snapshot. The FIRST failing
gate in precedence order determines the rejection reason; the signal validity
state follows §12 exact rules:

    Gate #1 UNAVAILABLE fails     → signal_validity = UNAVAILABLE
    Gate #2 INVALID fails         → signal_validity = INVALID
    Gate #3-#7 fails              → signal_validity = DEGRADED (no trade)
    All gates pass but degraded   → signal_validity = DEGRADED (trade allowed)
      (freshness < 0.50 ≥ 0.25, coverage 80-95%, regime_alignment 0.30-0.50)
    All gates pass, not degraded  → signal_validity = VALID

Patch P3: GateResult.signal_validity is assigned DIRECTLY to
Decision.signal_validity.
Patch P4: PIT validation is acceptance-tested against Layer 4 Synthetic
Datasets D (derived.available_time < max(inputs) → INVALID) and
D2 (derived.available_time == max(inputs) → passes Gate #2).
"""

from __future__ import annotations

from datetime import datetime

from ..contracts.decision import DecisionContext, RejectionReason, SignalValidity
from .result import GATE_PRECEDENCE, GateResult, GateState

DATA_QUALITY_THRESHOLD = 0.60
ECONOMIC_FILTER_THRESHOLD = 1.0
CORRELATION_THRESHOLD = 0.70
REGIME_ALIGNMENT_THRESHOLD = 0.30


class HardGateEngine:
    """Evaluates the seven hard gates in strict precedence order (§8)."""

    def evaluate(self, decision_context: DecisionContext) -> GateResult:
        ctx = decision_context
        gate_results: dict[GateState, bool] = {}

        # ---- Gate #1: UNAVAILABLE ----------------------------------------
        model_available = ctx.model_loaded and not ctx.required_data_missing
        vix_missing = ctx.vix is None
        unavailable_failed = (not model_available) or vix_missing
        gate_results[GateState.UNAVAILABLE] = not unavailable_failed
        unavailable_reason = (
            RejectionReason.VIX_UNAVAILABLE
            if vix_missing and model_available
            else RejectionReason.MODEL_UNAVAILABLE
        )

        # ---- Gate #2: INVALID ---------------------------------------------
        invalid_reason: RejectionReason | None = None
        if self._has_pit_violation(ctx):
            invalid_reason = RejectionReason.PIT_VIOLATION
        elif not self._component_scores_in_bounds(ctx):
            invalid_reason = RejectionReason.SIGNAL_OUT_OF_BOUNDS
        elif ctx.required_minimum_edge <= 0:
            invalid_reason = RejectionReason.INVALID_EDGE_THRESHOLD
        gate_results[GateState.INVALID] = invalid_reason is None

        # ---- Gate #3: CONCENTRATION (current >= max → FAIL) ---------------
        concentration_failed = ctx.current_exposure >= ctx.max_exposure
        gate_results[GateState.CONCENTRATION] = not concentration_failed

        # ---- Gate #4: DATA QUALITY (score < 0.60 → FAIL) ------------------
        dq_failed = ctx.data_quality_score is not None and ctx.data_quality_score < DATA_QUALITY_THRESHOLD
        gate_results[GateState.DATA_QUALITY] = not dq_failed

        # ---- Gate #5: ECONOMIC FILTER (edge_ratio < 1.0 → FAIL) -----------
        edge_failed = ctx.edge_ratio is None or ctx.edge_ratio < ECONOMIC_FILTER_THRESHOLD
        gate_results[GateState.ECONOMIC_FILTER] = not edge_failed

        # ---- Gate #6: CORRELATION (max_abs_correlation > 0.70 → FAIL) -----
        correlation_failed = (
            ctx.max_abs_correlation is not None
            and ctx.max_abs_correlation > CORRELATION_THRESHOLD
        )
        gate_results[GateState.CORRELATION] = not correlation_failed

        # ---- Gate #7: REGIME MISALIGNMENT (alignment < 0.30 → FAIL) -------
        regime_failed = (
            ctx.regime_alignment is not None
            and ctx.regime_alignment < REGIME_ALIGNMENT_THRESHOLD
        )
        gate_results[GateState.REGIME_MISALIGNMENT] = not regime_failed

        first_failing = next(
            (g for g in GATE_PRECEDENCE if not gate_results[g]), None
        )
        all_passed = first_failing is None

        # ---- Signal validity (§12) ---------------------------------------
        rejection_reason: RejectionReason | None = None
        if not gate_results[GateState.UNAVAILABLE]:
            signal_validity = SignalValidity.UNAVAILABLE
            rejection_reason = unavailable_reason
        elif not gate_results[GateState.INVALID]:
            signal_validity = SignalValidity.INVALID
            rejection_reason = invalid_reason
        elif not all_passed:
            signal_validity = SignalValidity.DEGRADED
            rejection_reason = self._reason_for_gate(first_failing)
        else:
            damaged = self._degraded_warnings(ctx)
            if damaged:
                signal_validity = SignalValidity.DEGRADED
            else:
                signal_validity = SignalValidity.VALID
            rejection_reason = None

        return GateResult(
            gate_results=gate_results,
            all_passed=all_passed,
            first_failing_gate=first_failing,
            thresholds_used={
                "data_quality": DATA_QUALITY_THRESHOLD,
                "economic_filter": ECONOMIC_FILTER_THRESHOLD,
                "correlation": CORRELATION_THRESHOLD,
                "regime_misalignment": REGIME_ALIGNMENT_THRESHOLD,
                "concentration": ctx.max_exposure,
            },
            signal_validity=signal_validity,
            rejection_reason=rejection_reason,
            degraded_warnings=self._degraded_warnings(ctx) if all_passed else [],
        )

    # ------------------------------------------------------------------
    # Gate #2 helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _has_pit_violation(ctx: DecisionContext) -> bool:
        inputs = ctx.input_available_times
        if inputs:
            latest_input = max(inputs)
            if not _tz_aware(latest_input) or not _tz_aware(ctx.prediction_timestamp):
                return True
            # PIT-1: any input available AFTER the prediction timestamp
            if any(t > ctx.prediction_timestamp for t in inputs):
                return True
            # PIT-2: derived.available_time MUST equal max(inputs) (Patch P4)
            if ctx.derived_available_time is not None:
                if ctx.derived_available_time != latest_input:
                    return True
        elif ctx.derived_available_time is not None:
            # No inputs declared — derived must not precede the prediction.
            if ctx.derived_available_time > ctx.prediction_timestamp:
                return True
        return False

    @staticmethod
    def _component_scores_in_bounds(ctx: DecisionContext) -> bool:
        for score in (ctx.quant_score, ctx.macro_score, ctx.rag_score):
            if score is not None and not (-1.0 <= score <= 1.0):
                return False
        return True

    @staticmethod
    def _reason_for_gate(gate: GateState | None) -> RejectionReason | None:
        if gate is None:
            return None
        return {
            GateState.CONCENTRATION: RejectionReason.CONCENTRATION_LIMIT,
            GateState.DATA_QUALITY: RejectionReason.DATA_QUALITY_DEGRADED,
            GateState.ECONOMIC_FILTER: RejectionReason.INSUFFICIENT_EDGE,
            GateState.CORRELATION: RejectionReason.CORRELATION_FILTER,
            GateState.REGIME_MISALIGNMENT: RejectionReason.REGIME_MISALIGNMENT,
        }.get(gate)

    @staticmethod
    def _degraded_warnings(ctx: DecisionContext) -> list[str]:
        """§12 degraded conditions evaluated when all gates pass."""
        warnings: list[str] = []
        if ctx.data_coverage_pct is not None and (
            0.80 <= ctx.data_coverage_pct < 0.95
        ):
            warnings.append("data_coverage degraded (>= 80% but < 95%)")
        if ctx.age_hours is not None:
            freshness = max(0.0, min(1.0, pow(2.718281828459045, -ctx.age_hours / 24.0)))
            if 0.25 <= freshness < 0.50:
                warnings.append("freshness degraded (>= 0.25 but < 0.50)")
        if ctx.regime_alignment is not None and (
            0.30 <= ctx.regime_alignment < 0.50
        ):
            warnings.append("regime_alignment in degraded band (0.30-0.50)")
        return warnings


def _tz_aware(value: datetime) -> bool:
    return value.tzinfo is not None and value.tzinfo.utcoffset(value) is not None