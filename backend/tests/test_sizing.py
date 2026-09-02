"""Prompt 9 — Position sizing (§11, Patch P7: secondary capacity safety)."""

from __future__ import annotations

import pytest

from meridian_fx.decision.contracts import RejectionReason, SignalValidity
from meridian_fx.decision.gates.result import GateResult, GateState
from meridian_fx.decision.sizing import PositionSizingEngine

engine = PositionSizingEngine()


def test_full_multiplier_path():
    result = engine.calculate(
        actionable=True,
        all_gates_passed=True,
        rejection_reason=None,
        base_size=100_000.0,
        edge_ratio=3.0,
        decision_quality=0.7668,
        vix=15.0,
        current_exposure=0.0,
        max_exposure=1_000_000.0,
    )
    assert result.multipliers.edge == 2.0  # capped at 2.0
    assert result.multipliers.quality == pytest.approx(0.7668)
    assert result.multipliers.volatility == pytest.approx(20.0 / (15.0 + 10.0))
    expected_pre = 100_000.0 * 2.0 * 0.7668 * 0.8
    assert result.position_size == pytest.approx(min(expected_pre, 1_000_000.0))


def test_volatility_multiplier_clipped():
    result = engine.calculate(True, True, None, 100_000.0, 1.5, 0.8, 100.0, 0.0, 1_000_000.0)
    assert result.multipliers.volatility == pytest.approx(0.25)  # floor
    result = engine.calculate(True, True, None, 100_000.0, 1.5, 0.8, 5.0, 0.0, 1_000_000.0)
    assert result.multipliers.volatility == pytest.approx(1.25)  # ceiling


def test_not_actionable_zero_position():
    result = engine.calculate(
        actionable=False,
        all_gates_passed=False,
        rejection_reason=RejectionReason.INSUFFICIENT_EDGE,
        base_size=100_000.0,
        edge_ratio=0.5,
        decision_quality=0.8,
        vix=15.0,
        current_exposure=0.0,
        max_exposure=1_000_000.0,
    )
    assert result.position_size == 0.0
    assert result.rejection_reason == RejectionReason.INSUFFICIENT_EDGE


def test_capacity_exhausted_concentration_limit():
    result = engine.calculate(
        actionable=True,
        all_gates_passed=True,
        rejection_reason=None,
        base_size=100_000.0,
        edge_ratio=1.5,
        decision_quality=0.8,
        vix=15.0,
        current_exposure=1_000_000.0,
        max_exposure=1_000_000.0,
    )
    assert result.position_size == 0.0
    assert result.rejection_reason == RejectionReason.CONCENTRATION_LIMIT


def test_capacity_cap_applied():
    result = engine.calculate(
        actionable=True,
        all_gates_passed=True,
        rejection_reason=None,
        base_size=100_000.0,
        edge_ratio=2.0,
        decision_quality=1.0,
        vix=15.0,
        current_exposure=900_000.0,
        max_exposure=1_000_000.0,
    )
    assert result.position_size == pytest.approx(100_000.0)  # = available capacity
    assert result.capacity_constrained is True


def test_vix_none_zero_position():
    result = engine.calculate(
        actionable=True, all_gates_passed=True, rejection_reason=None,
        base_size=100_000.0, edge_ratio=1.5, decision_quality=0.8,
        vix=None, current_exposure=0.0, max_exposure=1_000_000.0,
    )
    assert result.position_size == 0.0
    assert result.rejection_reason == RejectionReason.VIX_UNAVAILABLE


class TestPatchP7SecondarySafety:
    def test_gate_result_never_modified(self):
        gate = GateResult(
            gate_results={g: True for g in GateState},
            all_passed=True,
            first_failing_gate=None,
            thresholds_used={"concentration": 1_000_000.0, "data_quality": 0.6, "economic_filter": 1.0, "correlation": 0.7, "regime_misalignment": 0.3},
            signal_validity=SignalValidity.VALID,
            rejection_reason=None,
        )
        before = gate.model_dump()
        engine.calculate(
            actionable=True,
            all_gates_passed=gate.all_passed,
            rejection_reason=gate.rejection_reason,
            base_size=100_000.0,
            edge_ratio=2.0,
            decision_quality=0.9,
            vix=15.0,
            current_exposure=50_000.0,  # capacity check is SECONDARY
            max_exposure=1_000_000.0,
        )
        assert gate.model_dump() == before  # untouched

    def test_eligibility_vs_allocation_distinct(self):
        # Eligibility comes from Gate #3; allocation from available capacity.
        capacity_result = engine.calculate(
            actionable=True, all_gates_passed=True, rejection_reason=None,
            base_size=100_000.0, edge_ratio=2.0, decision_quality=1.0, vix=15.0,
            current_exposure=0.0, max_exposure=50_000.0,
        )
        assert capacity_result.position_size == pytest.approx(50_000.0)  # truncated
        assert capacity_result.rejection_reason is None