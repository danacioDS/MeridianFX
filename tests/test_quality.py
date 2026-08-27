"""Prompt 7 — Decision quality (§9, Patch P5/P6)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from meridian_fx.decision.contracts import DataQualityStatus
from meridian_fx.decision.quality import (
    DecisionQualityComponents,
    DecisionQualityEngine,
    QualityLevel,
)

UTC = timezone.utc
engine = DecisionQualityEngine()


def test_formula_direct():
    quality = engine.compute_direct(
        confidence=0.5705,
        age_hours=3.0,
        regime_alignment=0.825,
        data_quality_score=0.90,
        drift_psi=0.05,
    )
    expected = 0.3 * 0.5705 + 0.25 * engine.freshness_from_age(3.0) + 0.2 * 0.825 + 0.15 * 0.90 + 0.1 * 0.75
    assert quality.score == pytest.approx(expected, abs=1e-6)


def test_freshness_decay():
    assert engine.freshness_from_age(0.0) == pytest.approx(1.0)
    assert engine.freshness_from_age(24.0) == pytest.approx(0.3679, abs=1e-4)


def test_levels():
    assert engine.compute_direct(confidence=1.0, age_hours=0.5, regime_alignment=1.0, data_quality_score=1.0).level == QualityLevel.HIGH
    assert engine.compute_direct(confidence=0.6, age_hours=6.0, regime_alignment=0.5, data_quality_score=0.5, drift_psi=0.1).level == QualityLevel.MODERATE
    assert engine.compute_direct(confidence=0.1, age_hours=48.0, regime_alignment=0.2, data_quality_score=0.2, drift_psi=0.5).level == QualityLevel.LOW


def test_drift_fallback_when_psi_missing():
    quality = engine.compute_direct(
        confidence=0.9, age_hours=1.0, regime_alignment=0.9, data_quality_score=0.9, drift_psi=None
    )
    assert quality.components.drift_score == pytest.approx(0.50)
    assert quality.fallback_status.drift == "FALLBACK"


def test_drift_psi_above_threshold_saturates_to_zero():
    quality = engine.compute_direct(
        confidence=0.9, age_hours=1.0, regime_alignment=0.9, data_quality_score=0.9, drift_psi=5.0
    )
    assert quality.components.drift_score == pytest.approx(0.0)


class TestPatchP6StatusMapping:
    def test_mapping_boundaries(self):
        assert engine._status_from_score(0.85) == "good"
        assert engine._status_from_score(0.80) == "good"
        assert engine._status_from_score(0.70) == "acceptable"
        assert engine._status_from_score(0.60) == "acceptable"
        assert engine._status_from_score(0.50) == "degraded"

    def test_components_carry_status(self):
        quality = engine.compute_direct(
            confidence=0.9, age_hours=1.0, regime_alignment=0.9, data_quality_score=0.70
        )
        assert quality.components.data_quality == "acceptable"

    def test_inconsistent_status_rejected(self):
        with pytest.raises(ValidationError):
            DecisionQualityComponents(
                confidence=0.9,
                freshness=0.9,
                regime_alignment=0.9,
                data_quality="good",  # inconsistent with score 0.5 (Patch P6)
                data_quality_score=0.5,
                drift_score=0.9,
            )


class TestPatchP5Layer4Consumption:
    def test_computes_from_l4_registries(self, store, dq_registry, freshness_registry, drift_registry):
        as_of = datetime(2026, 1, 5, 10, 30, tzinfo=UTC)
        quality = engine.compute_from_providers(
            as_of=as_of,
            confidence=0.7,
            regime_alignment=0.8,
            data_quality_registry=dq_registry,
            freshness_registry=freshness_registry,
            drift_registry=drift_registry,
        )
        assert 0.0 <= quality.score <= 1.0
        assert quality.components.data_quality_score == pytest.approx(0.90)

    def test_missing_data_quality_raises(self, store, freshness_registry, drift_registry):
        class EmptyRegistry:
            version = "empty"
            def get_data_quality(self, as_of):
                return None

        with pytest.raises(ValueError):
            engine.compute_from_providers(
                as_of=datetime(2026, 1, 5, tzinfo=UTC),
                confidence=0.7,
                regime_alignment=0.8,
                data_quality_registry=EmptyRegistry(),
                freshness_registry=freshness_registry,
                drift_registry=drift_registry,
            )