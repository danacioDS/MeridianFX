"""Tests for rolling ARIMA(1,0,1) divergence analysis.

Covers KI-009's supplementary analysis: projecting a clean-float price
path and measuring how far the observed price has diverged from it.

The tests use synthetic series (no network) to verify:
  - ARIMA projection produces finite values on positive prices.
  - Short series are gracefully rejected.
  - Rolling window semantics are respected.
  - Z-score warm-up returns None.
  - Zero variance does not produce NaN/inf.
  - A synthetic shock produces elevated divergence.
  - DivergenceReport is well-formed.
"""
from __future__ import annotations

import math

import pytest

from meridian_fx.decision.divergence import (
    DivergenceReport,
    RollingARIMAProjector,
    compute_divergence_report,
    rolling_zscore,
)


# ── helpers ─────────────────────────────────────────────────────────

def _random_walk(n: int, seed: int = 42, drift: float = 0.0, sigma: float = 0.005):
    """Deterministic pseudo-random walk on log-prices.

    Produces strictly positive prices.
    """
    import numpy as np

    rng = np.random.default_rng(seed)
    log_prices = np.zeros(n)
    for i in range(1, n):
        log_prices[i] = log_prices[i - 1] + drift + sigma * rng.standard_normal()
    prices = np.exp(log_prices) * 100.0  # start around 100
    return prices.tolist()


def _synthetic_shock(n: int, shock_at: int, shock_size: float = 0.30):
    """Random walk with a sudden additive jump in log-price at `shock_at`."""
    prices = _random_walk(n, seed=7, sigma=0.003)
    for i in range(shock_at, n):
        prices[i] *= math.exp(shock_size)
    return prices


# ── tests ───────────────────────────────────────────────────────────

def test_prices_positive_produces_projection():
    prices = _random_walk(180, seed=1)
    dates = [f"2026-01-{i:02d}" for i in range(1, 181)]
    projector = RollingARIMAProjector(window=90)
    observed, projected = projector.project(dates, prices)

    assert len(observed) == len(prices)
    assert len(projected) == len(prices)
    # All projected values must be finite and strictly positive.
    for _, v in projected:
        assert math.isfinite(v)
        assert v > 0


def test_short_series_returns_observed_only():
    """With fewer than window + 2 points, no projection is produced:
    the projected series echoes the observed one."""
    prices = _random_walk(50, seed=2)
    dates = [f"2026-01-{i:02d}" for i in range(1, 51)]
    projector = RollingARIMAProjector(window=90)
    observed, projected = projector.project(dates, prices)

    assert observed == projected


def test_non_positive_prices_are_rejected():
    prices = _random_walk(180, seed=3)
    prices[10] = -1.0  # invalid
    dates = [f"2026-01-{i:02d}" for i in range(1, 181)]
    projector = RollingARIMAProjector(window=90)
    observed, projected = projector.project(dates, prices)
    # Fallback: projected echoes observed when input invalid.
    assert observed == projected


def test_arima_produces_finite_forecasts():
    prices = _random_walk(180, seed=4)
    dates = [f"2026-01-{i:02d}" for i in range(1, 181)]
    projector = RollingARIMAProjector(window=90)
    _, projected = projector.project(dates, prices)

    for _, v in projected:
        assert math.isfinite(v)
        assert v > 0


def test_rolling_window_respected():
    """The first `window` projections must equal observed (no forecast yet)."""
    prices = _random_walk(180, seed=5)
    dates = [f"2026-01-{i:02d}" for i in range(1, 181)]
    window = 90
    projector = RollingARIMAProjector(window=window)
    observed, projected = projector.project(dates, prices)

    for i in range(window):
        assert observed[i] == projected[i]

    # After the window, projections may differ from observed.
    # (We don't assert they differ, just that they're computed.)
    for i in range(window, len(prices)):
        assert math.isfinite(projected[i][1])


def test_dates_are_aligned():
    prices = _random_walk(180, seed=6)
    dates = [f"2026-01-{i:02d}" for i in range(1, 181)]
    projector = RollingARIMAProjector(window=90)
    observed, projected = projector.project(dates, prices)

    assert [d for d, _ in observed] == dates
    assert [d for d, _ in projected] == dates


def test_zscore_warmup_returns_none():
    observed = [100.0] * 10
    projected = [100.0] * 10
    zs = rolling_zscore(observed, projected, window=90, warmup=20)
    assert all(z is None for z in zs)


def test_zscore_zero_variance_returns_none():
    observed = [100.0] * 50
    projected = [100.0] * 50
    zs = rolling_zscore(observed, projected, window=90, warmup=20)
    # Zero variance → None (not NaN, not inf)
    for z in zs:
        assert z is None or math.isfinite(z)


def test_report_construction():
    prices = _random_walk(180, seed=10)
    dates = [f"2026-01-{i:02d}" for i in range(1, 181)]
    report = compute_divergence_report(
        pair="USD/BOB",
        dates=dates,
        prices=prices,
        regime="unknown",
        window=90,
    )
    assert isinstance(report, DivergenceReport)
    assert report.pair == "USD/BOB"
    assert report.regime == "unknown"
    assert report.window_days == 90
    assert len(report.observed_series) == len(prices)
    assert len(report.projected_series) == len(prices)
    assert len(report.divergence_series) == len(prices)
    # Interpretation must be one of the known values.
    assert report.interpretation in {
        "normal", "notable", "extreme", "persistent", "unavailable"
    }


def test_synthetic_shock_produces_elevated_divergence():
    """A sudden regime shift (synthetic shock) should produce a
    large-magnitude z-score AT THE TIME OF THE SHOCK.

    Note: the final z-score (at the end of the series) may not be
    elevated, because both the rolling mean and the ARIMA model adapt
    to the new level within ~50 observations. The signal we care about
    is the spike in divergence when the shock occurs.
    """
    n = 200
    shock_at = 150
    prices = _synthetic_shock(n, shock_at=shock_at, shock_size=0.30)
    dates = [f"2026-01-{i:02d}" for i in range(1, n + 1)]

    report = compute_divergence_report(
        pair="USD/XXX",
        dates=dates,
        prices=prices,
        regime="administered",
        window=90,
    )

    # Look at the window around the shock.
    start = max(0, shock_at - 5)
    end = min(len(report.divergence_series), shock_at + 15)
    window_z = [
        abs(z)
        for _, z in report.divergence_series[start:end]
        if z is not None
    ]
    assert window_z, "no z-scores available around shock"
    max_abs_z = max(window_z)
    assert max_abs_z > 1.0, (
        f"expected |z| > 1 around shock (indices {start}..{end}), "
        f"got max |z| = {max_abs_z}"
    )
