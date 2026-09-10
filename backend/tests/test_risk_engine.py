"""Unit tests for RiskEngine v2.3.0 — mathematical verification only.

These tests do NOT exercise the pipeline. They verify the frozen
methodology and normalization rules in isolation.
"""

from __future__ import annotations

import pytest

from backend.src.meridian_fx.decision.risk.engine import (
    RiskEngine,
    W_EDGE,
    W_MACRO,
    W_MODEL,
    W_REGIME,
    W_VOLATILITY,
)
from backend.src.meridian_fx.decision.risk.models import (
    METHODOLOGY_VERSION,
    RiskAssessment,
    RiskLevel,
)


@pytest.fixture
def engine() -> RiskEngine:
    return RiskEngine()


class TestWeights:
    def test_weights_sum_to_one(self):
        total = W_VOLATILITY + W_MACRO + W_MODEL + W_REGIME + W_EDGE
        assert total == pytest.approx(1.0)


class TestNormalizations:
    def test_volatility_low(self, engine):
        # VIX = 10 → 0.0
        a = engine.compute(vix=10.0, macro_status="FULL", confidence=1.0,
                           regime="Expansion", edge_ratio=5.0)
        vol = next(d for d in a.drivers if d.name == "volatility")
        assert vol.normalized_value == 0.0

    def test_volatility_high(self, engine):
        # VIX = 30 → 1.0
        a = engine.compute(vix=30.0, macro_status="FULL", confidence=1.0,
                           regime="Expansion", edge_ratio=5.0)
        vol = next(d for d in a.drivers if d.name == "volatility")
        assert vol.normalized_value == 1.0

    def test_volatility_clipped(self, engine):
        # VIX = 100 → clipped at 1.0
        a = engine.compute(vix=100.0, macro_status="FULL", confidence=1.0,
                           regime="Expansion", edge_ratio=5.0)
        vol = next(d for d in a.drivers if d.name == "volatility")
        assert vol.normalized_value == 1.0

    def test_volatility_none(self, engine):
        # VIX None → 1.0
        a = engine.compute(vix=None, macro_status="FULL", confidence=1.0,
                           regime="Expansion", edge_ratio=5.0)
        vol = next(d for d in a.drivers if d.name == "volatility")
        assert vol.normalized_value == 1.0

    def test_macro_full(self, engine):
        a = engine.compute(vix=15.0, macro_status="FULL", confidence=1.0,
                           regime="Expansion", edge_ratio=5.0)
        m = next(d for d in a.drivers if d.name == "macro")
        assert m.normalized_value == 0.0

    def test_macro_partial(self, engine):
        a = engine.compute(vix=15.0, macro_status="PARTIAL", confidence=1.0,
                           regime="Expansion", edge_ratio=5.0)
        m = next(d for d in a.drivers if d.name == "macro")
        assert m.normalized_value == 0.5

    def test_macro_unavailable(self, engine):
        a = engine.compute(vix=15.0, macro_status="UNAVAILABLE", confidence=1.0,
                           regime="Expansion", edge_ratio=5.0)
        m = next(d for d in a.drivers if d.name == "macro")
        assert m.normalized_value == 1.0

    def test_model_confidence_one(self, engine):
        a = engine.compute(vix=15.0, macro_status="FULL", confidence=1.0,
                           regime="Expansion", edge_ratio=5.0)
        m = next(d for d in a.drivers if d.name == "model")
        assert m.normalized_value == 0.0

    def test_model_confidence_zero(self, engine):
        a = engine.compute(vix=15.0, macro_status="FULL", confidence=0.0,
                           regime="Expansion", edge_ratio=5.0)
        m = next(d for d in a.drivers if d.name == "model")
        assert m.normalized_value == 1.0

    def test_regime_unknown(self, engine):
        a = engine.compute(vix=15.0, macro_status="FULL", confidence=1.0,
                           regime="UNKNOWN", edge_ratio=5.0)
        r = next(d for d in a.drivers if d.name == "regime")
        assert r.normalized_value == 1.0

    def test_regime_known(self, engine):
        a = engine.compute(vix=15.0, macro_status="FULL", confidence=1.0,
                           regime="Expansion", edge_ratio=5.0)
        r = next(d for d in a.drivers if d.name == "regime")
        assert r.normalized_value == 0.0

    def test_edge_at_ceil(self, engine):
        # edge = 5 → 0.0
        a = engine.compute(vix=15.0, macro_status="FULL", confidence=1.0,
                           regime="Expansion", edge_ratio=5.0)
        e = next(d for d in a.drivers if d.name == "edge")
        assert e.normalized_value == 0.0

    def test_edge_above_ceil(self, engine):
        # edge = 100 → clipped at 0.0
        a = engine.compute(vix=15.0, macro_status="FULL", confidence=1.0,
                           regime="Expansion", edge_ratio=100.0)
        e = next(d for d in a.drivers if d.name == "edge")
        assert e.normalized_value == 0.0

    def test_edge_negative(self, engine):
        # edge = -10 → clipped at 1.0
        a = engine.compute(vix=15.0, macro_status="FULL", confidence=1.0,
                           regime="Expansion", edge_ratio=-10.0)
        e = next(d for d in a.drivers if d.name == "edge")
        assert e.normalized_value == 1.0


class TestRiskScore:
    def test_min_risk(self, engine):
        """All drivers at minimum → score = 0."""
        a = engine.compute(
            vix=10.0, macro_status="FULL", confidence=1.0,
            regime="Expansion", edge_ratio=5.0,
        )
        assert a.risk_score == pytest.approx(0.0)
        assert a.risk_level == RiskLevel.LOW

    def test_max_risk(self, engine):
        """All drivers at maximum → score = 100."""
        a = engine.compute(
            vix=30.0, macro_status="UNAVAILABLE", confidence=0.0,
            regime="UNKNOWN", edge_ratio=-100.0,
        )
        assert a.risk_score == pytest.approx(100.0)
        assert a.risk_level == RiskLevel.EXTREME

    def test_score_equals_sum_of_contributions(self, engine):
        a = engine.compute(
            vix=20.0, macro_status="PARTIAL", confidence=0.5,
            regime="Expansion", edge_ratio=2.5,
        )
        total = sum(d.contribution for d in a.drivers)
        assert a.risk_score == pytest.approx(total)


class TestRiskLevels:
    def test_low(self, engine):
        # All minima
        a = engine.compute(vix=10.0, macro_status="FULL", confidence=1.0,
                           regime="Expansion", edge_ratio=5.0)
        assert a.risk_level == RiskLevel.LOW

    def test_extreme(self, engine):
        # All maxima
        a = engine.compute(vix=30.0, macro_status="UNAVAILABLE", confidence=0.0,
                           regime="UNKNOWN", edge_ratio=-100.0)
        assert a.risk_level == RiskLevel.EXTREME


class TestContract:
    def test_methodology_version(self, engine):
        a = engine.compute(vix=15.0, macro_status="FULL", confidence=1.0,
                           regime="Expansion", edge_ratio=5.0)
        assert a.methodology_version == METHODOLOGY_VERSION

    def test_five_drivers(self, engine):
        a = engine.compute(vix=15.0, macro_status="FULL", confidence=1.0,
                           regime="Expansion", edge_ratio=5.0)
        names = sorted(d.name for d in a.drivers)
        assert names == ["edge", "macro", "model", "regime", "volatility"]

    def test_returns_risk_assessment(self, engine):
        a = engine.compute(vix=15.0, macro_status="FULL", confidence=1.0,
                           regime="Expansion", edge_ratio=5.0)
        assert isinstance(a, RiskAssessment)


    def test_boundary_25_is_moderate(self, engine):
        a = engine.compute(
            vix=10.0,
            macro_status="FULL",
            confidence=1.0,
            regime="Expansion",
            edge_ratio=5.0,
        )
        # Construct exact score through direct level classification.
        assert engine._level_for(25.0) == RiskLevel.MODERATE

    def test_boundary_50_is_high(self, engine):
        assert engine._level_for(50.0) == RiskLevel.HIGH

    def test_boundary_75_is_extreme(self, engine):
        assert engine._level_for(75.0) == RiskLevel.EXTREME
