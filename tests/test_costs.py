"""Prompt 5 — §7.2 transaction costs (Patch P2: VIX from L4 only)."""

from __future__ import annotations

import pytest

from meridian_fx.decision.contracts import FeatureValue
from meridian_fx.decision.filter import (
    CostCalculator,
    PairCategory,
    VixUnavailableError,
)
from meridian_fx.decision.validation.validate_integration import FakeFeatureStore


class TestCostCatalog:
    def test_category_for_pair(self):
        assert CostCalculator.category_for("USDJPY") == PairCategory.MAJOR
        assert CostCalculator.category_for("GBPUSD") == PairCategory.MINOR
        assert CostCalculator.category_for("USDMXN") == PairCategory.EMERGING
        assert CostCalculator.category_for("USDARS") == PairCategory.FRONTIER

    def test_unknown_pair_raises(self):
        with pytest.raises(ValueError):
            CostCalculator.category_for("XXXYYY")


class TestVixInterpolation:
    def test_bounds(self):
        assert CostCalculator.normalized_volatility(10) == 0.0
        assert CostCalculator.normalized_volatility(30) == 1.0
        assert CostCalculator.normalized_volatility(5) == 0.0  # clipped
        assert CostCalculator.normalized_volatility(50) == 1.0  # clipped

    def test_linear_interpolation(self):
        assert CostCalculator.normalized_volatility(15) == pytest.approx(0.25)

    def test_spread_lower_bound(self):
        breakdown = CostCalculator.calculate_total_cost("USDJPY", 10.0)
        assert breakdown.spread == pytest.approx(0.2)  # base_min at VIX=10

    def test_spread_upper_bound(self):
        breakdown = CostCalculator.calculate_total_cost("USDJPY", 30.0)
        assert breakdown.spread == pytest.approx(0.5)  # base_max at VIX=30

    def test_total_cost_decomposition(self):
        breakdown = CostCalculator.calculate_total_cost("USDJPY", 15.0)
        assert breakdown.slippage == pytest.approx(0.5 * 15.0 / 20.0)
        assert breakdown.commission == pytest.approx(0.5)
        assert breakdown.total_cost == pytest.approx(
            breakdown.spread + breakdown.slippage + breakdown.commission
        )

    def test_frontier_higher_costs(self):
        frontier = CostCalculator.calculate_total_cost("USDARS", 20.0)
        major = CostCalculator.calculate_total_cost("EURUSD", 20.0)
        assert frontier.total_cost > major.total_cost

    def test_vix_none_returns_unavailable_p2(self):
        with pytest.raises(VixUnavailableError):
            CostCalculator.calculate_total_cost("USDJPY", None)


class TestVixFromLayer4:
    def test_vix_from_feature_store(self):
        from datetime import datetime, timezone

        store = FakeFeatureStore(vix=18.0)
        as_of = datetime(2026, 1, 5, 10, 30, tzinfo=timezone.utc)
        assert CostCalculator.vix_from_feature_store("USDJPY", store, as_of=as_of) == pytest.approx(18.0)

    def test_vix_missing_raises(self):
        from datetime import datetime, timezone

        store = FakeFeatureStore(vix=None)
        with pytest.raises(VixUnavailableError):
            CostCalculator.vix_from_feature_store(
                "USDJPY", store, as_of=datetime(2026, 1, 5, tzinfo=timezone.utc)
            )

    def test_no_alternative_vix_source(self):
        # The ONLY ingestion path is FeatureStore.get_feature('vix', T) (Patch P2).
        from meridian_fx.decision.filter.costs import VIX_FEATURE_ID

        assert VIX_FEATURE_ID == "vix"