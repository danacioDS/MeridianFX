"""PIT audit — diagnostic tests for KI-002.

These tests do NOT verify that PIT is correct. They capture the current
structural behavior of the pipeline so that when KI-002 is fixed, the
changes are forced to be explicit: the assertions here will fail and
must be updated deliberately.

See KNOWN_ISSUES.md KI-002 for the full diagnosis.

⚠️  These tests are DIAGNOSTIC. They document the current state. When
    KI-002-A / KI-002-B / KI-002-C are resolved, the assertions must be
    inverted or removed together with the fix.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from meridian_fx.decision.contracts import PredictionArtifact
from meridian_fx.decision.contracts.prediction import (
    ConfidenceInterval,
    MacroRegime,
    Reproducibility,
)

UTC = timezone.utc


def _make_artifact_at_wall_clock() -> PredictionArtifact:
    """Replicates the DecisionEngineAdapter pattern: one timestamp for
    every temporal field.

    This mirrors decision_engine_adapter.get_prediction_artifact() as of
    the state documented in KI-002-A. Do NOT change this fixture until
    the adapter itself is fixed.
    """
    timestamp = datetime(2026, 1, 5, 10, 30, tzinfo=UTC)
    return PredictionArtifact(
        prediction_id="pit-audit-1",
        model_id="logistic_USD_CHF",
        model_version="logistic-v1.0",
        pair="USD/CHF",
        prediction_timestamp=timestamp,
        horizon_days=5,
        probability_up=0.6,
        expected_return=10.0,
        expected_volatility=0.05,
        confidence_interval=ConfidenceInterval(lower=0.2, upper=0.4),
        regime_id="regime-test",
        macro_regime=MacroRegime(
            risk="Risk-On", policy="Neutral", growth="High", inflation="Low"
        ),
        feature_snapshot_id="snapshot-1",
        dataset_id="dataset-1",
        feature_version="1.0",
        as_of=timestamp,
        reproducibility=Reproducibility(
            git_commit="test",
            docker_image="test",
            mlflow_run_id="test",
        ),
        created_at=timestamp,
    )


def test_ki_002_a_as_of_collapses_with_prediction_timestamp():
    """KI-002-A diagnostic.

    The adapter pattern collapses as_of, prediction_timestamp and
    created_at into a single wall-clock value. This contradicts the
    Layer 3 contract ("as_of: knowledge point for this prediction"),
    which requires as_of <= prediction_timestamp and, in a real system,
    likely as_of < prediction_timestamp.

    When KI-002-A is fixed, replace this diagnostic assertion with a
    test proving that `as_of` comes from the propagated knowledge cutoff
    and is independent of the adapter's wall-clock generation time.

    The fix is not merely "as_of <= prediction_timestamp" — it is that
    `as_of` MUST be derived from temporal provenance (KI-002-D), not
    from `datetime.now()`.
    """
    artifact = _make_artifact_at_wall_clock()

    # Documents the collapse:
    assert artifact.as_of == artifact.prediction_timestamp
    assert artifact.as_of == artifact.created_at


def test_ki_002_c_input_available_times_makes_pit2_vacuous():
    """KI-002-C diagnostic.

    PipelineBridge populates input_available_times=[as_of]. With a
    single-element list, PIT-2 (derived.available_time =
    max(inputs.available_time)) reduces to a trivially true identity.

    This test documents the structure. When KI-002-C is fixed,
    input_available_times should carry the real per-input timestamps,
    and this test should assert that max(input_available_times) equals
    derived_available_time AND that the list contains more than one
    distinct input timestamp.
    """
    as_of = datetime(2026, 1, 5, 10, 30, tzinfo=UTC)
    input_available_times = [as_of]  # current PipelineBridge pattern
    derived_available_time = as_of

    # Documents the vacuous pass:
    assert max(input_available_times) == derived_available_time
    # And that the list is degenerate:
    assert len(set(input_available_times)) == 1
