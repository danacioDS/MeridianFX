"""Tests for exchange regime classification and forecast eligibility.

Covers KI-009: the exchange regime classifies how a currency pair's
price is determined (free float, managed float, administered, unknown),
and the forecast eligibility gate decides whether the pipeline may
produce a directional forecast for the pair.
"""
from __future__ import annotations

from meridian_fx.decision.contracts.exchange_regime import (
    EXCHANGE_REGIME_BY_PAIR,
    ExchangeRegime,
    ForecastEligibility,
    FundamentalCoverage,
    compute_forecast_eligibility,
    get_exchange_regime,
)


# ── get_exchange_regime ─────────────────────────────────────────────

def test_free_float_pairs_classified():
    for pair in ("USD/JPY", "EUR/USD", "GBP/USD", "USD/CHF", "USD/MXN", "USD/BRL"):
        assert get_exchange_regime(pair) == ExchangeRegime.FREE_FLOAT, pair


def test_managed_float_pair_classified():
    assert get_exchange_regime("USD/CNY") == ExchangeRegime.MANAGED_FLOAT


def test_unverified_pairs_are_unknown():
    """BOB and ARS are NOT classified as ADMINISTERED until verified
    against primary central bank sources (BCB, BCRA). They stay UNKNOWN.
    """
    assert get_exchange_regime("USD/BOB") == ExchangeRegime.UNKNOWN
    assert get_exchange_regime("USD/ARS") == ExchangeRegime.UNKNOWN


def test_unknown_pair_returns_unknown():
    assert get_exchange_regime("XXX/YYY") == ExchangeRegime.UNKNOWN
    assert get_exchange_regime("") == ExchangeRegime.UNKNOWN


# ── compute_forecast_eligibility ────────────────────────────────────

def test_free_float_is_eligible():
    assert compute_forecast_eligibility(ExchangeRegime.FREE_FLOAT) == ForecastEligibility.ELIGIBLE


def test_managed_float_is_restricted():
    assert compute_forecast_eligibility(ExchangeRegime.MANAGED_FLOAT) == ForecastEligibility.RESTRICTED


def test_administered_is_restricted():
    assert compute_forecast_eligibility(ExchangeRegime.ADMINISTERED) == ForecastEligibility.RESTRICTED


def test_unknown_regime_is_unknown_eligibility():
    assert compute_forecast_eligibility(ExchangeRegime.UNKNOWN) == ForecastEligibility.UNKNOWN


def test_insufficient_coverage_trumps_free_float():
    """Even for a free float, insufficient fundamental coverage means the
    system must not claim it can predict the pair.
    """
    assert (
        compute_forecast_eligibility(
            ExchangeRegime.FREE_FLOAT,
            FundamentalCoverage.INSUFFICIENT,
        )
        == ForecastEligibility.INSUFFICIENT_DATA
    )


def test_registry_has_no_duplicates():
    """The regime mapping must be internally consistent."""
    assert len(EXCHANGE_REGIME_BY_PAIR) == len(set(EXCHANGE_REGIME_BY_PAIR.keys()))
