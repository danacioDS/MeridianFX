"""Prompt 5 — §7.1 economic filter formula."""

from __future__ import annotations

import pytest

from meridian_fx.decision.contracts import Direction
from meridian_fx.decision.filter import (
    EconomicFilter,
    EdgeThresholdInvalidError,
)


def test_net_return_and_edge_long():
    result = EconomicFilter().apply(
        expected_return=20.0,
        direction=Direction.LONG,
        base_rate=1.0,
        quote_rate=0.1,
        horizon_days=5,
        total_cost=1.5,
        required_minimum_edge=10.0,
    )
    assert result.directional_gross_return == pytest.approx(20.0)
    assert result.carry_proxy == pytest.approx(1 * 0.9 * 5 / 365 * 10000)
    assert result.net_return == pytest.approx(20.0 + result.carry_proxy - 1.5)
    assert result.edge_ratio == pytest.approx(result.net_return / 10.0)
    assert result.actionable is True


def test_short_uses_negative_sign():
    result = EconomicFilter().apply(
        expected_return=20.0,
        direction=Direction.SHORT,
        base_rate=1.0,
        quote_rate=0.1,
        horizon_days=5,
        total_cost=1.5,
        required_minimum_edge=10.0,
    )
    assert result.directional_gross_return == pytest.approx(-20.0)
    # carry_proxy is already sign-adjusted for SHORT (base - quote < 0 side).
    assert result.carry_proxy == pytest.approx(-1 * 0.9 * 5 / 365 * 10000)
    assert result.net_return == pytest.approx(-20.0 + result.carry_proxy - 1.5)


def test_neutral_sign_zero():
    result = EconomicFilter().apply(
        expected_return=20.0,
        direction=Direction.NEUTRAL,
        base_rate=1.0,
        quote_rate=0.1,
        horizon_days=5,
        total_cost=1.5,
        required_minimum_edge=10.0,
    )
    assert result.directional_gross_return == 0.0
    assert result.carry_proxy == 0.0
    assert result.net_return == pytest.approx(-1.5)


def test_not_actionable_when_edge_below_one():
    result = EconomicFilter().apply(
        expected_return=5.0,
        direction=Direction.LONG,
        base_rate=0.0,
        quote_rate=0.0,
        horizon_days=5,
        total_cost=1.5,
        required_minimum_edge=10.0,
    )
    assert result.actionable is False


def test_required_minimum_edge_must_be_positive():
    with pytest.raises(EdgeThresholdInvalidError):
        EconomicFilter().apply(
            expected_return=20.0,
            direction=Direction.LONG,
            base_rate=1.0,
            quote_rate=0.1,
            horizon_days=5,
            total_cost=1.5,
            required_minimum_edge=0.0,
        )