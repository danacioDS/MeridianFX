"""Prompt 10 — Decision / Opportunity / SafeMode registries (Patch P8)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from meridian_fx.decision.contracts import (
    Decision,
    Direction,
    RejectionReason,
    SignalValidity,
)
from meridian_fx.decision.registries import (
    DecisionRegistry,
    OpportunityRegistry,
    OpportunityScoreInput,
    OpportunityScorer,
    RankedOpportunity,
    SafeModeConfig,
    SafeModeRegistry,
    SafeModeStateValue,
)

UTC = timezone.utc


def make_decision(decision_id="d-1", pair="USDJPY", actionable=True, **kw) -> Decision:
    defaults = dict(
        prediction_id="pred-1",
        pair=pair,
        timestamp=datetime(2026, 1, 5, 10, 31, tzinfo=UTC),
        as_of=datetime(2026, 1, 5, 10, 30, tzinfo=UTC),
        horizon_days=5,
        actionable=actionable,
        direction=Direction.LONG,
        confidence=0.6,
        edge_ratio=2.0,
        net_return=80.0,
        position_size=100_000.0,
        rejection_reason=None if actionable else RejectionReason.INSUFFICIENT_EDGE,
        signal_validity=SignalValidity.VALID if actionable else SignalValidity.DEGRADED,
    )
    defaults.update(kw)
    return Decision(decision_id=decision_id, **defaults)


class TestDecisionRegistryP8:
    def test_crud_api(self):
        registry = DecisionRegistry()
        d1 = make_decision("d-1")
        d2 = make_decision("d-2", pair="EURUSD")
        d3 = make_decision("d-3", pair="USDJPY", actionable=False)

        assert registry.store(d1) == "d-1"
        registry.store(d2)
        registry.store(d3)

        assert registry.get("d-1").decision_id == "d-1"
        assert registry.get("nope") is None
        assert registry.get_by_prediction("pred-1").decision_id in {"d-1", "d-2", "d-3"}
        assert len(registry.get_by_pair("USDJPY")) == 2
        assert registry.get_latest("USDJPY").decision_id == "d-3"
        assert [d.decision_id for d in registry.get_actionable("USDJPY")] == ["d-1"]

    def test_no_delivery_fields_stored(self):
        registry = DecisionRegistry()
        registry.store(make_decision("d-1"))
        stored = registry.get("d-1")
        for field in ("delivery_state", "delivery_reason", "delivery_warning"):
            assert not hasattr(stored, field), f"registry leaked {field}"

    def test_decision_model_itself_rejects_delivery_fields(self):
        with pytest.raises(ValidationError):
            make_decision(delivery_state="ELIGIBLE")


class TestOpportunity:
    def test_scorer_formula(self):
        window = [0.0, 0.1, 0.2, 0.3, 0.4, 0.44, 0.5, 0.52, 0.55, 0.58, 0.6, 0.61, 0.63, 0.65, 0.66, 0.68, 0.7, 0.72, 0.73, 0.75, 0.77, 0.78, 0.8, 0.82, 0.85, 0.88, 0.9, 0.93, 0.97, 1.0]
        result = OpportunityScorer().score(
            OpportunityScoreInput(
                fusion_score=0.27,
                risk_adj_return=0.6,
                decision_quality=0.77,
                max_abs_correlation=0.1,
                window=window,  # P5=0.0, P95=1.0 → normalized = 0.6
            )
        )
        # α=0.35, β=0.25, γ=0.25, δ=0.15
        expected = 0.35 * 0.27 + 0.25 * 0.6 + 0.25 * 0.77 + 0.15 * 0.9
        assert result.opportunity_score == pytest.approx(expected)
        assert result.normalization_status == "VALID"
        assert result.diversification_status == "VALID"

    def test_fallback_normalization(self):
        result = OpportunityScorer().score(
            OpportunityScoreInput(fusion_score=0.27, decision_quality=0.77, max_abs_correlation=None)
        )
        assert result.normalization_status == "FALLBACK"
        assert result.normalized_risk_adj_return == pytest.approx(0.5)
        assert result.diversification_status == "FALLBACK"
        assert result.diversification_benefit == pytest.approx(0.5)

    def test_short_window_fallback(self):
        result = OpportunityScorer().score(
            OpportunityScoreInput(fusion_score=0.27, decision_quality=0.77, window=list(range(10)))
        )
        assert result.normalization_status == "FALLBACK"

    def test_registry_ranks_descending(self):
        registry = OpportunityRegistry()
        registry.register(RankedOpportunity(rank=0, pair="USDJPY", direction=Direction.LONG, opportunity_score=0.5, edge_ratio=1.2, actionable=True, confidence=0.6, decision_quality=0.7, position_size=1.0, prediction_id="p1", decision_id="d1"))
        registry.register(RankedOpportunity(rank=0, pair="EURUSD", direction=Direction.LONG, opportunity_score=0.8, edge_ratio=1.5, actionable=True, confidence=0.7, decision_quality=0.8, position_size=1.0, prediction_id="p2", decision_id="d2"))
        assert registry.get_top().pair == "EURUSD"
        assert registry.get_ranking()[0].rank == 1
        assert registry.total_actionable() == 2


class TestSafeMode:
    def test_state_toggle(self):
        registry = SafeModeRegistry(SafeModeConfig(vix_floor=40.0))
        assert registry.get_state().state == SafeModeStateValue.OFF
        registry.activate("drift detected")
        assert registry.get_state().state == SafeModeStateValue.ON
        registry.release()
        assert registry.get_state().state == SafeModeStateValue.OFF

    def test_threshold_auto_activation(self):
        registry = SafeModeRegistry(SafeModeConfig(vix_floor=40.0, data_quality_floor=0.5))
        snapshot = registry.evaluate("USDJPY", datetime(2026, 1, 5, 10, 30, tzinfo=UTC), vix=45.0, data_quality_score=0.9)
        assert snapshot.state == SafeModeStateValue.ON
        assert snapshot.pair == "USDJPY"
        assert snapshot.as_of.tzinfo is not None

    def test_no_trigger_normal(self):
        registry = SafeModeRegistry(SafeModeConfig(vix_floor=40.0))
        snapshot = registry.evaluate("USDJPY", datetime(2026, 1, 5, 10, 30, tzinfo=UTC), vix=15.0, data_quality_score=0.9)
        assert snapshot.state == SafeModeStateValue.OFF