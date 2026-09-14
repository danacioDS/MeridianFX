"""Behavioral invariants of the MeridianFX decision pipeline.

Three groups:

A. Economic invariants (tests 1-3)
   The arithmetic contracts of the economic layer.

B. Narrative identity invariants (tests 4-6)
   The fingerprint contract of compute_narrative_key().

C. Decision reproducibility invariants (tests 7-8)
   The per-minute decision cache in PipelineBridge.

These tests are deterministic, network-free, and CI-safe.
"""
from __future__ import annotations

import copy
from datetime import datetime, timezone

import pytest

from meridian_fx.decision.contracts import Direction
from meridian_fx.decision.filter.economic import EconomicFilter

from backend.layer2.narrative.prompt_builder import (
    PROMPT_VERSION,
    compute_narrative_key,
)
from backend.layer2.pipeline_bridge import PipelineBridge


# ══════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════

def _base_decision_result() -> dict:
    return {
        "pair": "USD/CHF",
        "horizon_days": 5,
        "decision": {
            "pair": "USD/CHF",
            "horizon_days": 5,
            "direction": "SHORT",
            "signal_validity": "VALID",
            "actionable": True,
            "decision_id": "dec-aaa",
            "timestamp": "2026-09-14T22:00:00Z",
            "as_of": "2026-09-14T22:00:00Z",
        },
        "artifact": {
            "model_id": "logistic_USD_CHF",
            "model_version": "logistic-v1.0",
            "dataset_id": "dataset_20260914",
            "feature_version": "1.0",
            "created_at": "2026-09-14T22:00:00Z",
        },
        "economic": {
            "edge_ratio": 8.2417,
            "net_return": -88.18,
        },
        "macro_data_status": {"status": "FULL"},
    }


def _apply_filter(direction: Direction):
    """Call EconomicFilter.apply with the frozen signature.

    Rates are in PERCENT (1.0 = 1%). Costs are in bps.
    """
    return EconomicFilter().apply(
        expected_return=20.0,
        direction=direction,
        base_rate=1.0,
        quote_rate=0.1,
        horizon_days=5,
        total_cost=1.5,
        required_minimum_edge=10.0,
    )


# ══════════════════════════════════════════════════════════════════
# SECTION A — Economic invariants
# ══════════════════════════════════════════════════════════════════

def test_net_return_is_gross_plus_carry_minus_costs():
    """net_return = directional_gross_return + carry_proxy - total_cost.

    Must hold for LONG, SHORT, and NEUTRAL.
    """
    for direction in (Direction.LONG, Direction.SHORT, Direction.NEUTRAL):
        result = _apply_filter(direction)
        expected_net = (
            result.directional_gross_return
            + result.carry_proxy
            - result.total_cost
        )
        assert result.net_return == pytest.approx(expected_net, abs=1e-4), (
            f"direction={direction}: net_return mismatch"
        )


def test_edge_ratio_equals_net_return_over_required_min_edge():
    """edge_ratio = net_return / required_minimum_edge, for any direction."""
    for direction in (Direction.LONG, Direction.SHORT, Direction.NEUTRAL):
        result = _apply_filter(direction)
        assert result.edge_ratio == pytest.approx(
            result.net_return / result.required_minimum_edge, abs=1e-4
        ), f"direction={direction}: edge_ratio mismatch"


def test_actionable_iff_edge_at_least_one():
    """actionable <=> edge_ratio >= 1.0 — the economic-layer contract."""
    for direction in (Direction.LONG, Direction.SHORT, Direction.NEUTRAL):
        result = _apply_filter(direction)
        assert result.actionable == (result.edge_ratio >= 1.0), (
            f"direction={direction}: actionable/edge_ratio mismatch"
        )


# ══════════════════════════════════════════════════════════════════
# SECTION B — Narrative identity invariants
# ══════════════════════════════════════════════════════════════════

def test_narrative_key_is_deterministic():
    dr = _base_decision_result()
    k1 = compute_narrative_key(dr)
    k2 = compute_narrative_key(copy.deepcopy(dr))
    assert k1 == k2
    assert isinstance(k1, str) and len(k1) == 16


def test_narrative_key_changes_on_economic_change():
    dr = _base_decision_result()
    k1 = compute_narrative_key(dr)
    dr2 = copy.deepcopy(dr)
    dr2["economic"]["edge_ratio"] = 8.9999
    k2 = compute_narrative_key(dr2)
    assert k1 != k2


def test_narrative_key_ignores_timestamps_and_ids():
    dr = _base_decision_result()
    k1 = compute_narrative_key(dr)
    dr2 = copy.deepcopy(dr)
    dr2["decision"]["decision_id"] = "dec-bbb"
    dr2["decision"]["timestamp"] = "2099-01-01T00:00:00Z"
    dr2["decision"]["as_of"] = "2099-01-01T00:00:00Z"
    dr2["artifact"]["created_at"] = "2099-01-01T00:00:00Z"
    k2 = compute_narrative_key(dr2)
    assert k1 == k2, "fingerprint must ignore timestamps and opaque IDs"


def test_prompt_version_is_declared():
    assert isinstance(PROMPT_VERSION, str)
    assert PROMPT_VERSION.strip() != ""


# ══════════════════════════════════════════════════════════════════
# SECTION C — Decision reproducibility invariants
# ══════════════════════════════════════════════════════════════════

class _CallCounter:
    def __init__(self):
        self.calls = 0

    async def __call__(self, pair, horizon_days):
        self.calls += 1
        return {
            "pair": pair,
            "horizon_days": horizon_days,
            "decision": {"as_of": datetime.now(timezone.utc).isoformat()},
            "economic": {"net_return": 100.0 + self.calls},
            "artifact": {"model_id": "stub"},
            "macro_data_status": {"status": "FULL"},
        }


@pytest.fixture
def bridge_with_stub():
    import asyncio
    from datetime import timedelta

    bridge = PipelineBridge.__new__(PipelineBridge)
    counter = _CallCounter()
    bridge._evaluate_pair_uncached = counter  # type: ignore[assignment]
    bridge._decision_cache = {}
    bridge._cache_lock = asyncio.Lock()
    bridge._cache_ttl = timedelta(minutes=1)
    return bridge, counter


async def test_same_bucket_returns_cached_result(bridge_with_stub):
    bridge, counter = bridge_with_stub
    r1 = await bridge.evaluate_pair("USD/CHF", 5)
    r2 = await bridge.evaluate_pair("USD/CHF", 5)

    assert counter.calls == 1, "second call must hit the cache"
    assert r1["economic"]["net_return"] == r2["economic"]["net_return"]
    assert r1["_cache"]["hit"] is False
    assert r2["_cache"]["hit"] is True
    assert r1["_cache"]["bucket"] == r2["_cache"]["bucket"]


async def test_force_refresh_bypasses_cache(bridge_with_stub):
    bridge, counter = bridge_with_stub
    r1 = await bridge.evaluate_pair("USD/CHF", 5)
    assert counter.calls == 1
    r2 = await bridge.evaluate_pair("USD/CHF", 5, force_refresh=True)
    assert counter.calls == 2, "force_refresh must bypass the cache"
    assert r1["economic"]["net_return"] != r2["economic"]["net_return"]
    assert r2["_cache"]["hit"] is False
