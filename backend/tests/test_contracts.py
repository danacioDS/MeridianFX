"""Prompt 1 — Domain contract tests (Decision, PredictionArtifact, PIT-5)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from meridian_fx.decision.contracts import (
    REQUIRED_PREDICTION_FIELDS,
    Decision,
    Direction,
    PredictionArtifact,
    SignalValidity,
)
from meridian_fx.decision.contracts.prediction import ConfidenceInterval, MacroRegime

UTC = timezone.utc


def make_decision(**overrides) -> Decision:
    defaults = dict(
        decision_id="d-1",
        prediction_id="pred-1",
        pair="USDJPY",
        timestamp=datetime(2026, 1, 5, 10, 31, tzinfo=UTC),
        as_of=datetime(2026, 1, 5, 10, 30, tzinfo=UTC),
        horizon_days=5,
        actionable=True,
        direction=Direction.LONG,
        confidence=0.57,
        edge_ratio=2.5,
        net_return=142.1,
        position_size=100000.0,
        rejection_reason=None,
        signal_validity=SignalValidity.VALID,
    )
    defaults.update(overrides)
    return Decision(**defaults)


def test_decision_has_exact_prompt_1_field_set():
    d = make_decision()
    dumped = d.model_dump()
    expected = {
        "decision_id", "prediction_id", "pair", "timestamp", "as_of",
        "horizon_days", "actionable", "direction", "confidence",
        "edge_ratio", "net_return", "position_size", "rejection_reason",
        "signal_validity", "created_at",
    }
    assert set(dumped) == expected


def test_decision_rejects_naive_timestamps_pit5():
    with pytest.raises(ValidationError) as exc:
        make_decision(timestamp=datetime(2026, 1, 5, 10, 31))
    assert "naive" in str(exc.value)


def test_decision_rejects_confidence_out_of_range():
    with pytest.raises(ValidationError):
        make_decision(confidence=1.2)


def test_decision_rejects_extra_fields_including_layer1_delivery_p8():
    with pytest.raises(ValidationError):
        make_decision(delivery_state="ELIGIBLE")


def test_direction_and_validity_literals_enforced():
    d = make_decision()
    assert d.direction == Direction.LONG
    assert d.signal_validity == SignalValidity.VALID
    with pytest.raises(ValidationError):
        make_decision(direction="UP")
    with pytest.raises(ValidationError):
        make_decision(signal_validity="BANANA")


def test_prediction_artifact_covers_patch_p1_fields(artifact):
    for field in REQUIRED_PREDICTION_FIELDS:
        assert hasattr(artifact, field), f"missing PredictionArtifact.{field}"
    assert artifact.as_of.tzinfo is not None
    assert artifact.prediction_timestamp > artifact.as_of


def test_prediction_artifact_rejects_naive_timestamps():
    with pytest.raises(ValidationError):
        PredictionArtifact(
            prediction_id="p",
            model_id="m",
            model_version="v",
            pair="USDJPY",
            prediction_timestamp=datetime(2026, 1, 5, 10, 30),
            horizon_days=5,
            probability_up=0.6,
            expected_return=10.0,
            expected_volatility=0.05,
            confidence_interval=ConfidenceInterval(lower=0.2, upper=0.4),
            regime_id="r",
            macro_regime=MacroRegime(risk="Risk-On", policy="Neutral", growth="High", inflation="Low"),
            feature_snapshot_id="f",
            dataset_id="d",
            feature_version="1",
            as_of=datetime(2026, 1, 5, 10, 0),
        )