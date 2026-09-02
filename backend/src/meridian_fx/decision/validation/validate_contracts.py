"""Layer 2 contract validation (Prompt 12 — no structural changes).

Validates Layer 2 contracts against the FROZEN L1 (v5.1), L3 (v5.0) and
L4 (v3.1.1) interfaces, including patches P1, P3, P6, P8, P9.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from ..contracts import (
    REQUIRED_PREDICTION_FIELDS,
    Decision,
    PredictionArtifact,
    SignalValidity,
)
from ..registries import DecisionRegistry


class ValidationCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    passed: bool
    detail: str = ""


class ValidationReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target: str
    checks: list[ValidationCheck] = []

    @property
    def all_passed(self) -> bool:
        return all(c.passed for c in self.checks)

    def add(self, name: str, passed: bool, detail: str = "") -> None:
        self.checks.append(ValidationCheck(name=name, passed=passed, detail=detail))


def default_validity_to_delivery(validity: SignalValidity) -> str:
    """Default Decision → ForecastResponse delivery mapping (Patch P9).

        VALID       → ELIGIBLE
        DEGRADED    → NOT_ELIGIBLE (unless overridden by Layer 1 policy)
        INVALID     → NOT_ELIGIBLE
        UNAVAILABLE → UNAVAILABLE

    ``delivery_reason`` is a Layer 1 concern — NOT part of Decision.
    """
    return {
        SignalValidity.VALID: "ELIGIBLE",
        SignalValidity.DEGRADED: "NOT_ELIGIBLE",
        SignalValidity.INVALID: "NOT_ELIGIBLE",
        SignalValidity.UNAVAILABLE: "UNAVAILABLE",
    }[validity]


def validate_contract_suite(
    decisions: list[Decision] | None = None,
    artifacts: list[PredictionArtifact] | None = None,
    registry: DecisionRegistry | None = None,
) -> ValidationReport:
    """Runs the full Layer 2 contract validation suite."""
    report = ValidationReport(target="Layer 2 v3.4.1 contracts")

    # ---- CK-01: Decision mandatory fields (Prompt 1) ----------------------
    required_fields = (
        "decision_id", "prediction_id", "pair", "timestamp", "as_of",
        "horizon_days", "actionable", "direction", "confidence",
        "edge_ratio", "net_return", "position_size", "rejection_reason",
        "signal_validity", "created_at",
    )
    if decisions:
        missing = any(
            field not in (d.model_dump() if isinstance(d, Decision) else d)
            for d in decisions
            for field in required_fields
        )
        report.add(
            "CK-01 Decision mandatory fields", not missing,
            "Prompt 1 field set present and intact",
        )

    # ---- CK-02: signal_validity literal (Prompt 1) -------------------------
    if decisions:
        bad = [d for d in decisions if not SignalValidity.has_value(d.signal_validity)]
        report.add(
            "CK-02 signal_validity literal",
            not bad,
            f"decision.signal_validity in {[v.value for v in SignalValidity]}",
        )

    # ---- CK-03: confidence in [0, 1] ---------------------------------------
    if decisions:
        out_of_range = [d for d in decisions if not (0.0 <= d.confidence <= 1.0)]
        report.add("CK-03 confidence in [0, 1]", not out_of_range)

    # ---- CK-04: timestamps timezone-aware (PIT-5) --------------------------
    if decisions:
        naive = [
            d.decision_id
            for d in decisions
            if not _tz_aware(d.timestamp) or not _tz_aware(d.as_of)
        ]
        report.add("CK-04 timestamps tz-aware UTC (PIT-5)", not naive)

    # ---- CK-05: Patch P9 mapping table --------------------------------------
    mapping_ok = {
        "VALID": "ELIGIBLE",
        "DEGRADED": "NOT_ELIGIBLE",
        "INVALID": "NOT_ELIGIBLE",
        "UNAVAILABLE": "UNAVAILABLE",
    }
    mismatches = [
        (v, default_validity_to_delivery(SignalValidity(v)), expected)
        for v, expected in mapping_ok.items()
        if default_validity_to_delivery(SignalValidity(v)) != expected
    ]
    report.add(
        "CK-05 Patch P9 decision→delivery mapping", not mismatches,
        "VALID→ELIGIBLE, DEGRADED→NOT_ELIGIBLE, INVALID→NOT_ELIGIBLE, UNAVAILABLE→UNAVAILABLE",
    )

    # ---- CK-06: Patch P8 registry excludes Layer 1 delivery fields ---------
    if registry is not None:
        leaked = []
        for decision_id in list(registry._store):
            decision = registry.get(decision_id)
            for field in ("delivery_state", "delivery_reason", "delivery_warning"):
                if hasattr(decision, field):
                    leaked.append(field)
        report.add(
            "CK-06 Patch P8 no Layer 1 delivery fields stored", not leaked,
            "Registry stores signal_validity / rejection_reason only",
        )

    # ---- CK-07: Patch P1 PredictionArtifact reference completeness ---------
    if decisions and artifacts:
        by_id = {a.prediction_id: a for a in artifacts}
        incomplete = []
        for d in decisions:
            artifact = by_id.get(d.prediction_id)
            missing_fields = [
                f for f in REQUIRED_PREDICTION_FIELDS
                if artifact is None or not hasattr(artifact, f)
            ]
            if missing_fields:
                incomplete.append((d.prediction_id, missing_fields))
        report.add(
            "CK-07 Patch P1 Decision.prediction_id → complete PredictionArtifact",
            not incomplete,
            "probability_up, expected_return, expected_volatility, confidence_interval, "
            "shap_values, macro_regime, rag_signal_ids, feature_snapshot_id, dataset_id, "
            "as_of, model_id, model_version",
        )

    return report


def _tz_aware(value: datetime) -> bool:
    return value.tzinfo is not None and value.tzinfo.utcoffset(value) is not None