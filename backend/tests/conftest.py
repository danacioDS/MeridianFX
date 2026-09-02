"""Shared fixtures for the Layer 2 test suite.

Layer 4 providers below are test doubles implementing the frozen L4 v3.1.1
§7 protocol (Patch P5): Layer 2 never implements these registries.
"""

from __future__ import annotations

import pytest

from meridian_fx.decision.contracts import (
    ConfidenceInterval,
    DataQualitySnapshot,
    DriftSnapshot,
    FeatureValue,
    FreshnessSnapshot,
    MacroRegime,
    PredictionArtifact,
    Reproducibility,
    ShapValue,
)
from meridian_fx.decision.contracts.providers import DataQualityStatus
from meridian_fx.decision.validation.validate_integration import (
    FakeDataQualityRegistry,
    FakeDriftRegistry,
    FakeFeatureStore,
    FakeFreshnessRegistry,
)
from meridian_fx.decision.validation.validate_integration import (
    scenario_dataset_d,
    scenario_dataset_d2,
)


class FakeDataQualityRegistry2(FakeDataQualityRegistry):
    """Alias so tests may construct providers directly."""


@pytest.fixture
def store():
    return FakeFeatureStore(vix=15.0)


@pytest.fixture
def dq_registry():
    return FakeDataQualityRegistry(0.90)


@pytest.fixture
def freshness_registry():
    return FakeFreshnessRegistry(3.0)


@pytest.fixture
def drift_registry():
    return FakeDriftRegistry(0.05)


@pytest.fixture
def artifact() -> PredictionArtifact:
    from datetime import datetime, timedelta, timezone

    as_of = datetime(2026, 1, 5, 10, 30, tzinfo=timezone.utc)
    return PredictionArtifact(
        prediction_id="pred-1",
        model_id="ensemble_v3",
        model_version="3.4.1",
        pair="USDJPY",
        prediction_timestamp=as_of + timedelta(minutes=1),
        horizon_days=5,
        probability_up=0.65,
        expected_return=20.0,
        expected_volatility=0.06,
        confidence_interval=ConfidenceInterval(lower=0.35, upper=0.45),
        regime_id="regime-1",
        macro_regime=MacroRegime(
            risk="Risk-On", policy="Neutral", growth="High", inflation="Low"
        ),
        rag_signal_ids=["rag-1"],
        shap_values=[ShapValue(feature="us_10y", value=0.12)],
        feature_snapshot_id="snap-1",
        dataset_id="dataset_D2",
        feature_version="1.0",
        as_of=as_of,
        reproducibility=Reproducibility(
            git_commit="abc", docker_image="img", mlflow_run_id="run-1"
        ),
        created_at=as_of,
    )


@pytest.fixture
def dataset_d():
    return scenario_dataset_d()


@pytest.fixture
def dataset_d2():
    return scenario_dataset_d2()


__all__ = [
    "FakeFeatureStore",
    "FakeDataQualityRegistry",
    "FakeFreshnessRegistry",
    "FakeDriftRegistry",
]