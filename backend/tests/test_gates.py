"""Prompt 6 — Hard gates (precedence, thresholds, §12 validity).

Includes the MANDATORY Layer 4 Synthetic Dataset D / D2 acceptance tests
(Patch P4 / P10): D → Gate #2 INVALID, D2 → Gate #2 VALID.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from meridian_fx.decision.contracts import (
    DecisionContext,
    RejectionReason,
    SignalValidity,
)
from meridian_fx.decision.contracts.fusion import Direction
from meridian_fx.decision.gates import GateState, HardGateEngine
from meridian_fx.decision.validation.validate_integration import (
    scenario_dataset_d,
    scenario_dataset_d2,
)

UTC = timezone.utc
engine = HardGateEngine()


def make_context(**overrides) -> DecisionContext:
    defaults = dict(
        pair="USDJPY",
        prediction_timestamp=datetime(2026, 1, 5, 10, 31, tzinfo=UTC),
        as_of=datetime(2026, 1, 5, 10, 30, tzinfo=UTC),
        horizon_days=5,
        model_loaded=True,
        required_data_missing=False,
        vix=15.0,
        quant_score=0.3,
        macro_score=0.3,
        rag_score=0.15,
        required_minimum_edge=10.0,
        derived_available_time=datetime(2026, 1, 5, 10, 30, tzinfo=UTC),
        input_available_times=[
            datetime(2026, 1, 5, 10, 0, tzinfo=UTC),
            datetime(2026, 1, 5, 10, 30, tzinfo=UTC),
        ],
        current_exposure=0.0,
        max_exposure=1_000_000.0,
        data_quality_score=0.90,
        data_quality_status="good",
        expected_return=20.0,
        base_rate=1.0,
        quote_rate=0.1,
        direction=Direction.LONG,
        total_cost=1.5,
        edge_ratio=5.0,
        net_return=80.0,
        max_abs_correlation=0.1,
        regime_alignment=0.825,
    )
    defaults.update(overrides)
    return DecisionContext(**defaults)


def test_all_gates_pass_is_valid():
    result = engine.evaluate(make_context())
    assert result.all_passed
    assert result.signal_validity == SignalValidity.VALID
    assert result.first_failing_gate is None
    assert result.rejection_reason is None


class TestPrecedence:
    def test_unavailable_highest_precedence(self):
        result = engine.evaluate(
            make_context(vix=None, derived_available_time=datetime(2026, 1, 5, 9, 0, tzinfo=UTC))
        )
        assert result.first_failing_gate == GateState.UNAVAILABLE
        assert result.gate_results[GateState.UNAVAILABLE] is False
        assert result.signal_validity == SignalValidity.UNAVAILABLE
        assert result.rejection_reason == RejectionReason.VIX_UNAVAILABLE

    def test_model_not_loaded(self):
        result = engine.evaluate(make_context(model_loaded=False))
        assert result.first_failing_gate == GateState.UNAVAILABLE
        assert result.rejection_reason == RejectionReason.MODEL_UNAVAILABLE

    def test_invalid_beats_concentration(self):
        # Both Gate #2 (PIT) and Gate #3 (concentration) fail → INVALID wins.
        result = engine.evaluate(
            make_context(
                derived_available_time=datetime(2026, 1, 5, 10, 0, tzinfo=UTC),  # PIT-2
                current_exposure=2_000_000.0,  # concentration fail
            )
        )
        assert result.first_failing_gate == GateState.INVALID
        assert result.signal_validity == SignalValidity.INVALID

    def test_precedence_order_constant(self):
        assert tuple(GateState) == (
            GateState.UNAVAILABLE,
            GateState.INVALID,
            GateState.CONCENTRATION,
            GateState.DATA_QUALITY,
            GateState.ECONOMIC_FILTER,
            GateState.CORRELATION,
            GateState.REGIME_MISALIGNMENT,
        )


class TestIndividualGates:
    @pytest.mark.parametrize(
        "override,expected_gate,expected_reason,expected_validity",
        [
            (dict(current_exposure=1_500_000.0), GateState.CONCENTRATION, RejectionReason.CONCENTRATION_LIMIT, SignalValidity.DEGRADED),
            (dict(data_quality_score=0.50), GateState.DATA_QUALITY, RejectionReason.DATA_QUALITY_DEGRADED, SignalValidity.DEGRADED),
            (dict(edge_ratio=0.5), GateState.ECONOMIC_FILTER, RejectionReason.INSUFFICIENT_EDGE, SignalValidity.DEGRADED),
            (dict(max_abs_correlation=0.9), GateState.CORRELATION, RejectionReason.CORRELATION_FILTER, SignalValidity.DEGRADED),
            (dict(regime_alignment=0.20), GateState.REGIME_MISALIGNMENT, RejectionReason.REGIME_MISALIGNMENT, SignalValidity.DEGRADED),
        ],
    )
    def test_gate_failure_mapping(self, override, expected_gate, expected_reason, expected_validity):
        result = engine.evaluate(make_context(**override))
        assert result.first_failing_gate == expected_gate
        assert result.gate_results[expected_gate] is False
        assert result.rejection_reason == expected_reason
        assert result.signal_validity == expected_validity
        assert result.all_passed is False


class TestInvalidGate:
    def test_pit_1_violation_input_after_prediction(self):
        result = engine.evaluate(
            make_context(
                input_available_times=[
                    datetime(2026, 1, 5, 10, 0, tzinfo=UTC),
                    datetime(2026, 1, 5, 12, 0, tzinfo=UTC),  # > prediction_timestamp
                ]
            )
        )
        assert result.first_failing_gate == GateState.INVALID
        assert result.rejection_reason == RejectionReason.PIT_VIOLATION
        assert result.signal_validity == SignalValidity.INVALID

    def test_component_out_of_bounds(self):
        result = engine.evaluate(make_context(quant_score=1.5))
        assert result.first_failing_gate == GateState.INVALID
        assert result.rejection_reason == RejectionReason.SIGNAL_OUT_OF_BOUNDS

    def test_required_minimum_edge_non_positive(self):
        result = engine.evaluate(make_context(required_minimum_edge=0.0))
        assert result.first_failing_gate == GateState.INVALID
        assert result.rejection_reason == RejectionReason.INVALID_EDGE_THRESHOLD


class TestDegradedBands:
    def test_regime_alignment_warning_band(self):
        result = engine.evaluate(make_context(regime_alignment=0.40))
        assert result.all_passed is True
        assert result.signal_validity == SignalValidity.DEGRADED
        assert any("regime_alignment" in w for w in result.degraded_warnings)

    def test_freshness_warning_band(self):
        result = engine.evaluate(make_context(age_hours=24.0))  # freshness ≈ 0.368
        assert result.all_passed is True
        assert result.signal_validity == SignalValidity.DEGRADED

    def test_coverage_warning_band(self):
        result = engine.evaluate(make_context(data_coverage_pct=0.90))
        assert result.all_passed is True
        assert result.signal_validity == SignalValidity.DEGRADED


class TestMandatorySyntheticData:
    """Patch P4 / P10 — MUST pass for Layer 2 v1.1 acceptance."""

    def test_dataset_d_trigger_gate2_invalid(self, dataset_d):
        inputs = dataset_d
        assert inputs.derived_available_time < max(inputs.input_available_times)
        ctx = DecisionContext(
            pair=inputs.artifact.pair,
            prediction_timestamp=inputs.artifact.prediction_timestamp,
            as_of=inputs.artifact.as_of,
            horizon_days=inputs.artifact.horizon_days,
            vix=15.0,
            quant_score=0.3,
            macro_score=0.3,
            rag_score=0.15,
            required_minimum_edge=inputs.required_minimum_edge,
            derived_available_time=inputs.derived_available_time,
            input_available_times=inputs.input_available_times,
            data_quality_score=0.9,
            edge_ratio=5.0,
            regime_alignment=0.825,
            max_abs_correlation=0.1,
        )
        result = engine.evaluate(ctx)
        assert result.gate_results[GateState.INVALID] is False
        assert result.first_failing_gate == GateState.INVALID
        assert result.signal_validity == SignalValidity.INVALID
        assert result.rejection_reason == RejectionReason.PIT_VIOLATION

    def test_dataset_d2_passes_gate2(self, dataset_d2):
        inputs = dataset_d2
        assert inputs.derived_available_time == max(inputs.input_available_times)
        ctx = DecisionContext(
            pair=inputs.artifact.pair,
            prediction_timestamp=inputs.artifact.prediction_timestamp,
            as_of=inputs.artifact.as_of,
            horizon_days=inputs.artifact.horizon_days,
            vix=15.0,
            quant_score=0.3,
            macro_score=0.3,
            rag_score=0.15,
            required_minimum_edge=inputs.required_minimum_edge,
            derived_available_time=inputs.derived_available_time,
            input_available_times=inputs.input_available_times,
            data_quality_score=0.9,
            edge_ratio=5.0,
            regime_alignment=0.825,
            max_abs_correlation=0.1,
        )
        result = engine.evaluate(ctx)
        assert result.gate_results[GateState.INVALID] is True
        assert result.all_passed is True
        assert result.signal_validity == SignalValidity.VALID