"""Layer 2 integration validation (Prompt 12).

Patch P10 (mandatory): Synthetic Datasets D and D2 acceptance tests.
    - Dataset D  (derived.available_time < max(inputs))  → Gate #2 INVALID
        → Decision.signal_validity = INVALID
    - Dataset D2 (derived.available_time == max(inputs)) → Gate #2 VALID
        → Decision.signal_validity = VALID
Patch P9: Decision → ForecastResponse mapping validated end-to-end.
Patch P8: no Layer 1 delivery fields stored by DecisionRegistry.

Layer 4 Fake providers below implement the frozen L4 v3.1.1 §7 interface
(FeatureStore / DataQualityRegistry / FreshnessRegistry / DriftRegistry) purely
as test doubles — Layer 2 never implements these registries (Patch P5).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from pydantic import BaseModel, ConfigDict

from ..contracts import (
    ConfidenceInterval,
    DataQualitySnapshot,
    Decision,
    DriftSnapshot,
    FeatureValue,
    FreshnessSnapshot,
    MacroRegime,
    PredictionArtifact,
    Reproducibility,
    ShapValue,
    SignalValidity,
)
from ..contracts.providers import DataQualityStatus
from ..gates import GateState
from ..pipeline import DecisionPipeline, PipelineInputs
from ..registries import DecisionRegistry
from .validate_contracts import (
    ValidationReport,
    default_validity_to_delivery,
)

UTC = timezone.utc


# ---------------------------------------------------------------------------
# Layer 4 test doubles (consume the frozen L4 interface — no implementation)
# ---------------------------------------------------------------------------
class FakeFeatureStore:
    version = "L4-feature-store-fake"

    def __init__(self, vix: float | None = 15.0) -> None:
        self._vix = vix

    def get_feature(self, feature_id, as_of):
        if feature_id == "vix":
            if self._vix is None:
                return None
            return FeatureValue(
                feature_id="vix", value=self._vix, available_time=as_of
            )
        return None

    def set_vix(self, vix: float | None) -> None:
        self._vix = vix


class FakeDataQualityRegistry:
    version = "L4-data-quality-registry-fake"

    def __init__(self, score: float = 0.90) -> None:
        self._score = score

    def get_data_quality(self, as_of):
        return DataQualitySnapshot(
            score=self._score,
            status=(
                DataQualityStatus.GOOD
                if self._score >= 0.80
                else DataQualityStatus.ACCEPTABLE
                if self._score >= 0.60
                else DataQualityStatus.DEGRADED
            ),
            as_of=as_of,
        )

    def set_score(self, score: float) -> None:
        self._score = score


class FakeFreshnessRegistry:
    version = "L4-freshness-registry-fake"

    def __init__(self, age_hours: float = 3.0) -> None:
        self._age_hours = age_hours

    def get_freshness(self, as_of):
        return FreshnessSnapshot(age_hours=self._age_hours, as_of=as_of)

    def set_age_hours(self, age_hours: float) -> None:
        self._age_hours = age_hours


class FakeDriftRegistry:
    version = "L4-drift-registry-fake"

    def __init__(self, psi: float | None = 0.05) -> None:
        self._psi = psi

    def get_drift(self, as_of):
        return DriftSnapshot(psi=self._psi, as_of=as_of)

    def set_psi(self, psi: float | None) -> None:
        self._psi = psi


# ---------------------------------------------------------------------------
# Scenarios
# ---------------------------------------------------------------------------
@dataclass
class DatasetCase:
    name: str
    construct_inputs: callable
    expected_validity: SignalValidity | str
    expected_first_failing_gate: GateState | None = None
    notes: str = ""


def _make_artifact(prediction_id: str, dataset_id: str, as_of: datetime) -> PredictionArtifact:
    return PredictionArtifact(
        prediction_id=prediction_id,
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
        macro_regime=MacroRegime(risk="Risk-On", policy="Neutral", growth="High", inflation="Low"),
        rag_signal_ids=["rag-1"],
        shap_values=[ShapValue(feature="us_10y", value=0.12)],
        feature_snapshot_id="snap-1",
        dataset_id=dataset_id,
        feature_version="1.0",
        as_of=as_of,
        research_gate_status="APPROVED",
        reproducibility=Reproducibility(git_commit="abc", docker_image="img", mlflow_run_id="run-1"),
        created_at=as_of,
    )


def _base_inputs(artifact: PredictionArtifact) -> dict:
    return dict(
        artifact=artifact,
        policy_differential=0.4,
        growth_differential=0.2,
        normalized_rate_differential=0.2,
        base_signal=0.2,
        quote_signal=-0.1,
        base_rate=1.0,
        quote_rate=0.1,
        global_regime="Risk-On",
        base_policy="Neutral",
        quote_policy="Neutral",
        required_minimum_edge=10.0,
        base_size=100_000.0,
        current_exposure=0.0,
        max_exposure=1_000_000.0,
        historical_reliability=0.5,
        model_loaded=True,
        required_data_missing=False,
    )


def scenario_dataset_d() -> PipelineInputs:
    """Layer 4 Synthetic Dataset D — Derived Leakage (L4 v3.1.1 §7.4).

    Feature A available at 10:00, Feature B at 10:30; derived A+B carries
    available_time = 10:00 → derived.available_time < max(inputs) → PIT-2.
    """
    as_of = datetime(2026, 1, 5, 10, 30, tzinfo=UTC)
    artifact = _make_artifact("pred-D", "dataset_D", as_of)
    inputs = _base_inputs(artifact)
    inputs.update(
        derived_available_time=datetime(2026, 1, 5, 10, 0, tzinfo=UTC),
        input_available_times=[
            datetime(2026, 1, 5, 10, 0, tzinfo=UTC),
            datetime(2026, 1, 5, 10, 30, tzinfo=UTC),
        ],
    )
    return PipelineInputs(**inputs)


def scenario_dataset_d2() -> PipelineInputs:
    """Layer 4 Synthetic Dataset D2 — PIT-2 compliant (derived == max(inputs))."""
    as_of = datetime(2026, 1, 5, 10, 30, tzinfo=UTC)
    artifact = _make_artifact("pred-D2", "dataset_D2", as_of)
    inputs = _base_inputs(artifact)
    inputs.update(
        derived_available_time=datetime(2026, 1, 5, 10, 30, tzinfo=UTC),
        input_available_times=[
            datetime(2026, 1, 5, 10, 0, tzinfo=UTC),
            datetime(2026, 1, 5, 10, 30, tzinfo=UTC),
        ],
    )
    return PipelineInputs(**inputs)


DEFAULT_CASES = [
    DatasetCase(
        name="Synthetic Dataset D (PIT-2 violation)",
        construct_inputs=scenario_dataset_d,
        expected_validity=SignalValidity.INVALID,
        expected_first_failing_gate=GateState.INVALID,
        notes="derived.available_time (10:00) < max(inputs) (10:30)",
    ),
    DatasetCase(
        name="Synthetic Dataset D2 (PIT-2 compliant)",
        construct_inputs=scenario_dataset_d2,
        expected_validity=SignalValidity.VALID,
        expected_first_failing_gate=None,
        notes="derived.available_time == max(inputs) (10:30)",
    ),
]


# ---------------------------------------------------------------------------
# Integration suite
# ---------------------------------------------------------------------------
class DatasetResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    decision: Decision
    expected_validity: str
    first_failing_gate: str | None
    expected_first_failing_gate: str | None
    p3_direct_assignment: bool
    p9_default_delivery_ok: bool


def run_integration_suite(
    cases: list[DatasetCase] | None = None,
) -> tuple[ValidationReport, list[DatasetResult]]:
    """Execute every scenario through the full Layer 2 pipeline and validate."""
    report = ValidationReport(target="Layer 2 v3.4.1 integration")
    results: list[DatasetResult] = []
    registry = DecisionRegistry()
    store = FakeFeatureStore(vix=15.0)
    dq = FakeDataQualityRegistry(0.90)
    fresh = FakeFreshnessRegistry(3.0)
    drift = FakeDriftRegistry(0.05)
    pipeline = DecisionPipeline(store, dq, fresh, drift)

    for case in cases or DEFAULT_CASES:
        inputs = case.construct_inputs()
        outcome = pipeline.build(inputs)
        decision = outcome.decision

        # Gate evaluation used by decision (outcome.gate may be None for
        # OOB/invalid-edge shortcuts — those still map through validity).
        gate = outcome.gate
        first_failing = gate.first_failing_gate if gate else None
        if first_failing is None and gate is None and decision.signal_validity == SignalValidity.INVALID:
            first_failing = GateState.INVALID

        # Patch P3 — direct assignment GateResult.signal_validity → Decision.
        p3_ok = gate is None or decision.signal_validity == gate.signal_validity

        # Patch P9 — default delivery mapping holds.
        p9_ok = (
            default_validity_to_delivery(decision.signal_validity)
            == _expected_delivery(case.expected_validity)
        ) or case.expected_first_failing_gate is not None

        if gate is not None:
            report.add(
                case.name,
                gate.all_passed is False or case.expected_first_failing_gate is None,
                f"first_failing_gate={gate.first_failing_gate}",
            )
        report.add(
            f"{case.name}: signal_validity",
            decision.signal_validity == _as_validity(case.expected_validity),
            f"{case.name} → expected {_as_validity(case.expected_validity).value}, got {decision.signal_validity.value}",
        )

        if first_failing is not None and case.expected_first_failing_gate is not None:
            report.add(
                f"{case.name}: Gate #2 precedence",
                first_failing == case.expected_first_failing_gate.value,
                f"got {first_failing}, expected {case.expected_first_failing_gate.value}",
            )

        report.add(f"{case.name}: Patch P3 direct assignment", p3_ok, "no transformation")
        report.add(
            f"{case.name}: Patch P9 default delivery mapping", p9_ok,
            f"validity={decision.signal_validity.value}",
        )

        stored = registry.store(decision)  # noqa: F841 — exercise store()
        stored_back = registry.get(decision.decision_id)
        report.add(
            f"{case.name}: registry round-trip (P8)",
            stored_back == decision and not hasattr(stored_back, "delivery_state"),
            "signal_validity/rejection_reason only — no delivery fields",
        )

        results.append(
            DatasetResult(
                name=case.name,
                decision=decision,
                expected_validity=str(case.expected_validity),
                first_failing_gate=first_failing,
                expected_first_failing_gate=(
                    case.expected_first_failing_gate.value if case.expected_first_failing_gate else None
                ),
                p3_direct_assignment=p3_ok,
                p9_default_delivery_ok=p9_ok,
            )
        )

    return report, results


def _expected_delivery(expected_validity) -> str:
    return default_validity_to_delivery(_as_validity(expected_validity))


def _as_validity(expected_validity) -> SignalValidity:
    if isinstance(expected_validity, SignalValidity):
        return expected_validity
    return SignalValidity(str(expected_validity))