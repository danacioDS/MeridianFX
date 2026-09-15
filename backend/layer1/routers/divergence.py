"""Divergence Router — rolling ARIMA(1,0,1) divergence analysis.

Exposes /v1/fx/{pair}/regime-divergence, which projects the price of a
pair under a clean-float ARIMA(1,0,1) rolling one-step-ahead model and
measures how far the observed price has diverged.

Use case: for pairs in administered or managed-float regimes, the
observed price is not determined by market forces. This endpoint shows
the divergence between the observed price and what a clean-float model
would have projected, as a proxy for intervention.

See KNOWN_ISSUES.md KI-009 for context.
"""
from __future__ import annotations

from fastapi import APIRouter, Path, Query

from backend.layer2.data.provider import DataProvider
from backend.layer1.utils.pair_normalizer import normalize_pair
from backend.src.meridian_fx.decision.contracts.exchange_regime import (
    get_exchange_regime,
)
from backend.src.meridian_fx.decision.divergence import (
    compute_divergence_report,
)


router = APIRouter(tags=["divergence"])

data_provider = DataProvider()


@router.get("/{pair:path}/regime-divergence")
async def get_regime_divergence(
    pair: str = Path(..., description="Currency pair, e.g. USD/BOB"),
    window_days: int = Query(
        90,
        ge=30,
        le=365,
        description="Rolling window in days for ARIMA and z-score",
    ),
    period: str = Query(
        "1y",
        description="Historical period to fetch",
    ),
):
    """Rolling ARIMA(1,0,1) divergence between observed and projected price.

    The projected series is the one-step-ahead forecast of a
    clean-float ARIMA(1,0,1) model, rolled forward over the historical
    window. The z-score measures how many rolling standard deviations
    the current divergence is from its recent mean.
    """
    pair = pair.upper()
    normalized_pair = normalize_pair(pair)

    # Fetch historical data
    try:
        result = data_provider.get_historical(
            pair,
            period=period,
            interval="1d",
        )
    except Exception as exc:
        return {
            "error": "Data fetch failed",
            "pair": normalized_pair,
            "detail": str(exc)[:200],
        }

    df = result["data"]
    if df.empty:
        return {
            "error": "No data available",
            "pair": normalized_pair,
        }

    # Extract dates and close prices
    dates = [idx.strftime("%Y-%m-%d") for idx in df.index]
    prices = [float(row["Close"]) for _, row in df.iterrows()]

    # Determine exchange regime
    regime = get_exchange_regime(normalized_pair).value

    # Compute divergence report
    report = compute_divergence_report(
        pair=normalized_pair,
        dates=dates,
        prices=prices,
        regime=regime,
        window=window_days,
    )

    # Serialize
    return {
        "pair": report.pair,
        "regime": report.regime,
        "window_days": report.window_days,
        "current_zscore": report.current_zscore,
        "interpretation": report.interpretation,
        "observed_series": [
            [d, v] for d, v in report.observed_series
        ],
        "projected_series": [
            [d, v] for d, v in report.projected_series
        ],
        "divergence_series": [
            [d, v] for d, v in report.divergence_series
        ],
        "metadata": {
            "provider": result["provider"],
            "freshness": result["freshness"],
            "last_date": result["last_date"].isoformat(),
            "n_observations": len(prices),
        },
    }
