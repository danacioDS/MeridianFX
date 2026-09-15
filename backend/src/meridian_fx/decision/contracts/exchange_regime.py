"""Exchange regime classification and forecast eligibility (v3.0 scaffolding).

Distinguishes a currency pair's exchange-rate regime from its macro
regime (`contracts/regime.py`). The macro regime classifies the
economic environment (Goldilocks, Expansion, Crisis). The exchange
regime classifies how the pair's price is determined:

    FREE_FLOAT       — market-determined (EUR/USD, USD/JPY, ...)
    MANAGED_FLOAT    — central bank intervenes periodically (USD/CNY)
    ADMINISTERED     — central bank fixes or heavily administers the rate
    UNKNOWN          — not yet verified against a primary source

Rationale: the current Logistic_24 model uses 23 technical features
plus 1 macro feature (`policy_diff`). For administered-regime pairs,
technical analysis of the market price is not informative because the
price does not clear through market forces. Producing directional
forecasts for those pairs is economically incorrect.

This module introduces a pre-model gate:

    regime + fundamental_coverage  →  forecast_eligibility

Forecast eligibility is checked BEFORE the pipeline runs. If a pair
is not eligible, the pipeline returns a RESTRICTED decision with an
explicit reason. No silent hiding.

See KNOWN_ISSUES.md KI-009 for context.
"""
from __future__ import annotations

from enum import StrEnum


class ExchangeRegime(StrEnum):
    """Exchange-rate regime of a currency pair."""

    FREE_FLOAT = "free_float"
    MANAGED_FLOAT = "managed_float"
    ADMINISTERED = "administered"
    UNKNOWN = "unknown"


class FundamentalCoverage(StrEnum):
    """Coverage of fundamental features for a pair.

    The current Logistic_24 model only uses technical + policy_diff
    features. For pairs where fundamental data is essential (administered
    regimes), the coverage is insufficient until the fundamental pipeline
    is built (v3.0).
    """

    SUFFICIENT = "sufficient"
    INSUFFICIENT = "insufficient"
    UNKNOWN = "unknown"


class ForecastEligibility(StrEnum):
    """Whether the system may produce a directional forecast for a pair."""

    ELIGIBLE = "eligible"
    RESTRICTED = "restricted"
    INSUFFICIENT_DATA = "insufficient_data"
    UNKNOWN = "unknown"


# ── Pair classification ─────────────────────────────────────────────
#
# WARNING: This mapping is PROVISIONAL. It has NOT been verified against
# primary central bank sources. Pairs marked UNKNOWN are deliberately
# left unclassified until the source documentation is in place.
#
# Do NOT classify USD/BOB or USD/ARS as ADMINISTERED without a primary
# source from the respective central bank (BCB, BCRA) with an effective
# date. The regime change in Bolivia (June 2026) is not yet verified in
# the codebase.

EXCHANGE_REGIME_BY_PAIR: dict[str, ExchangeRegime] = {
    # G10 free floats
    "USD/JPY": ExchangeRegime.FREE_FLOAT,
    "EUR/USD": ExchangeRegime.FREE_FLOAT,
    "GBP/USD": ExchangeRegime.FREE_FLOAT,
    "USD/CHF": ExchangeRegime.FREE_FLOAT,
    # EM free floats
    "USD/MXN": ExchangeRegime.FREE_FLOAT,
    "USD/BRL": ExchangeRegime.FREE_FLOAT,
    # Managed float (PBOC manages the yuan within a band)
    "USD/CNY": ExchangeRegime.MANAGED_FLOAT,
    # Administered / unverified — kept UNKNOWN until primary source
    "USD/ARS": ExchangeRegime.UNKNOWN,
    "USD/BOB": ExchangeRegime.UNKNOWN,
}


def get_exchange_regime(pair: str) -> ExchangeRegime:
    """Return the classified exchange regime for a pair.

    Unknown pairs (not in the mapping) are returned as UNKNOWN.
    """
    return EXCHANGE_REGIME_BY_PAIR.get(pair, ExchangeRegime.UNKNOWN)


def compute_forecast_eligibility(
    regime: ExchangeRegime,
    fundamental_coverage: FundamentalCoverage = FundamentalCoverage.UNKNOWN,
) -> ForecastEligibility:
    """Determine whether the pipeline may produce a forecast for a pair.

    Rules:
      - UNKNOWN regime → UNKNOWN (do not guess)
      - ADMINISTERED regime → RESTRICTED (technical model cannot predict)
      - MANAGED_FLOAT regime → RESTRICTED (need fundamental features first)
      - INSUFFICIENT fundamental coverage → INSUFFICIENT_DATA
      - otherwise → ELIGIBLE
    """
    if regime == ExchangeRegime.UNKNOWN:
        return ForecastEligibility.UNKNOWN
    if regime == ExchangeRegime.ADMINISTERED:
        return ForecastEligibility.RESTRICTED
    if regime == ExchangeRegime.MANAGED_FLOAT:
        return ForecastEligibility.RESTRICTED
    if fundamental_coverage == FundamentalCoverage.INSUFFICIENT:
        return ForecastEligibility.INSUFFICIENT_DATA
    return ForecastEligibility.ELIGIBLE


__all__ = [
    "ExchangeRegime",
    "FundamentalCoverage",
    "ForecastEligibility",
    "EXCHANGE_REGIME_BY_PAIR",
    "get_exchange_regime",
    "compute_forecast_eligibility",
]
