"""Prompt 12 — Contract validation suite + mandatory D/D2 integration acceptance."""

from __future__ import annotations

from meridian_fx.decision.contracts import Direction, RejectionReason, SignalValidity
from meridian_fx.decision.registries import DecisionRegistry
from meridian_fx.decision.validation.validate_contracts import (
    default_validity_to_delivery,
    validate_contract_suite,
)
from meridian_fx.decision.validation.validate_integration import (
    run_integration_suite,
    scenario_dataset_d,
    scenario_dataset_d2,
)


class TestContractSuite:
    def test_clean_decision_passes_all_checks(self, dataset_d2):
        registry = DecisionRegistry()
        pipeline = _pipeline()
        decision = pipeline.build(dataset_d2).decision
        registry.store(decision)
        report = validate_contract_suite(
            decisions=[decision], artifacts=[dataset_d2.artifact], registry=registry
        )
        assert report.all_passed, report.model_dump()
        assert len(report.checks) == 7  # CK-01 … CK-07


class TestPatchP9Mapping:
    def test_mapping_table(self):
        assert default_validity_to_delivery(SignalValidity.VALID) == "ELIGIBLE"
        assert default_validity_to_delivery(SignalValidity.DEGRADED) == "NOT_ELIGIBLE"
        assert default_validity_to_delivery(SignalValidity.INVALID) == "NOT_ELIGIBLE"
        assert default_validity_to_delivery(SignalValidity.UNAVAILABLE) == "UNAVAILABLE"


class TestMandatoryIntegrationSuite:
    """Patch P10 — the two mandatory Synthetic Datasets run the FULL pipeline."""

    def test_default_suite_all_passed(self, store, dq_registry, freshness_registry, drift_registry):
        report, results = run_integration_suite()
        assert len(results) == 2
        assert [r.name for r in results] == [
            "Synthetic Dataset D (PIT-2 violation)",
            "Synthetic Dataset D2 (PIT-2 compliant)",
        ]
        assert report.all_passed, report.model_dump()
        for result in results:
            assert result.p3_direct_assignment is True
            assert result.p9_default_delivery_ok is True
            assert result.decision.signal_validity == result.expected_validity

    def test_dataset_d_result_details(self):
        _, results = run_integration_suite()
        d = results[0]
        assert d.expected_validity == "INVALID"
        assert d.first_failing_gate == "invalid"
        assert d.decision.rejection_reason == RejectionReason.PIT_VIOLATION
        assert d.decision.actionable is False

    def test_dataset_d2_result_details(self):
        _, results = run_integration_suite()
        d2 = results[1]
        assert d2.decision.signal_validity == SignalValidity.VALID
        assert d2.first_failing_gate is None
        assert d2.decision.actionable is True
        assert d2.decision.direction == Direction.LONG


def _pipeline():
    from meridian_fx.decision.pipeline import DecisionPipeline
    from meridian_fx.decision.validation.validate_integration import (
        FakeDataQualityRegistry,
        FakeDriftRegistry,
        FakeFeatureStore,
        FakeFreshnessRegistry,
    )

    return DecisionPipeline(
        FakeFeatureStore(15.0),
        FakeDataQualityRegistry(0.90),
        FakeFreshnessRegistry(3.0),
        FakeDriftRegistry(0.05),
    )