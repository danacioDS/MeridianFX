"""Layer 2 pipeline integration tests (orchestration glue, no new contracts)."""

from __future__ import annotations

from meridian_fx.decision.contracts import Direction, RejectionReason, SignalValidity
from meridian_fx.decision.gates import GateState
from meridian_fx.decision.pipeline import DecisionPipeline
from meridian_fx.decision.validation.validate_integration import (
    FakeDataQualityRegistry,
    FakeDriftRegistry,
    FakeFeatureStore,
    FakeFreshnessRegistry,
    scenario_dataset_d,
    scenario_dataset_d2,
)


def build_pipeline(store=None, dq=None, fresh=None, drift=None):
    return DecisionPipeline(
        store or FakeFeatureStore(15.0),
        dq or FakeDataQualityRegistry(0.90),
        fresh or FakeFreshnessRegistry(3.0),
        drift or FakeDriftRegistry(0.05),
    )


def test_happy_path_end_to_end(dataset_d2):
    outcome = build_pipeline().build(dataset_d2)
    decision = outcome.decision
    assert decision.signal_validity == SignalValidity.VALID
    assert decision.actionable is True
    assert decision.direction == Direction.LONG
    assert decision.position_size > 0
    assert decision.rejection_reason is None
    assert decision.prediction_id == "pred-D2"
    assert outcome.gate is not None and outcome.gate.all_passed
    assert outcome.vix == 15.0
    assert outcome.regime == "Goldilocks"
    assert outcome.sizing["position_size"] == decision.position_size

    # Patch P3: Decision.signal_validity assigned DIRECTLY from GateResult.
    assert decision.signal_validity == outcome.gate.signal_validity


def test_dataset_d_invalid_end_to_end(dataset_d):
    decision = build_pipeline().build(dataset_d).decision
    assert decision.signal_validity == SignalValidity.INVALID
    assert decision.actionable is False
    assert decision.rejection_reason == RejectionReason.PIT_VIOLATION
    assert decision.position_size == 0.0

    outcome = build_pipeline().build(dataset_d)
    assert outcome.gate.first_failing_gate == GateState.INVALID


def test_vix_unavailable_propagates(dataset_d2):
    pipeline = build_pipeline(store=FakeFeatureStore(vix=None))
    decision = pipeline.build(dataset_d2).decision
    assert decision.signal_validity == SignalValidity.UNAVAILABLE
    assert decision.rejection_reason == RejectionReason.VIX_UNAVAILABLE
    assert decision.actionable is False
    assert decision.position_size == 0.0


def test_degraded_quality_gate(dataset_d2):
    pipeline = build_pipeline(dq=FakeDataQualityRegistry(0.50))
    outcome = pipeline.build(dataset_d2)
    assert outcome.gate.first_failing_gate == GateState.DATA_QUALITY
    assert outcome.decision.signal_validity == SignalValidity.DEGRADED
    assert outcome.decision.actionable is False


def test_insufficient_edge_frontier_pair():
    """Pair costs (frontier) erase the edge → economic gate fails."""
    from datetime import datetime, timedelta, timezone

    from meridian_fx.decision.contracts import (
        ConfidenceInterval,
        MacroRegime,
        PredictionArtifact,
    )

    as_of = datetime(2026, 1, 5, 10, 30, tzinfo=timezone.utc)
    artifact = PredictionArtifact(
        prediction_id="p-edge",
        model_id="m",
        model_version="1",
        pair="USDARS",
        prediction_timestamp=as_of + timedelta(minutes=1),
        horizon_days=5,
        probability_up=0.51,
        expected_return=0.5,  # bps — below frontier costs
        expected_volatility=0.05,
        confidence_interval=ConfidenceInterval(lower=0.4, upper=0.6),
        regime_id="r",
        macro_regime=MacroRegime(risk="Risk-On", policy="Neutral", growth="High", inflation="Low"),
        feature_snapshot_id="f",
        dataset_id="d",
        feature_version="1",
        as_of=as_of,
    )
    inputs = scenario_dataset_d2()
    inputs.artifact = artifact
    inputs.base_rate = 0.0  # kill carry so costs dominate the edge
    inputs.quote_rate = 0.0
    decision = build_pipeline().build(inputs).decision
    assert decision.signal_validity == SignalValidity.DEGRADED
    assert decision.rejection_reason == RejectionReason.INSUFFICIENT_EDGE
    assert decision.position_size == 0.0


def test_out_of_bounds_signal_short_circuits():
    inputs = scenario_dataset_d2()
    inputs.policy_differential = 3.0  # macro_score = 1.5 → OOB → Gate #2 INVALID
    decision = build_pipeline().build(inputs).decision
    assert decision.signal_validity == SignalValidity.INVALID
    assert decision.rejection_reason == RejectionReason.SIGNAL_OUT_OF_BOUNDS


def test_safe_mode_integration(dataset_d2):
    from meridian_fx.decision.contracts import utcnow
    from meridian_fx.decision.registries import SafeModeConfig, SafeModeRegistry

    registry = SafeModeRegistry(SafeModeConfig(vix_floor=40.0))
    decision = build_pipeline(store=FakeFeatureStore(45.0)).build(dataset_d2).decision
    snapshot = registry.evaluate(decision.pair, utcnow(), vix=45.0, data_quality_score=0.9)
    assert snapshot.state.value == "ON"  # safety daemon observes high-VIX state