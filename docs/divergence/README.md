# Regime Divergence Analysis

**Date:** 2026-09-15
**Status:** implemented (backend + endpoint)
**Related:** KNOWN_ISSUES.md KI-009

## Problem

For currency pairs in administered or managed-float regimes, the
observed price is not determined by market forces. Technical analysis
of the price series is therefore not informative — the price does not
clear through supply and demand.

Detecting these regimes without fundamental data is possible using a
statistical proxy: project what a clean-float price path *would* look
like, and measure how far the observed path has diverged.

## Method

### Rolling ARIMA(1,0,1) projection

On daily **log-returns**:

    r[t] = c + phi * r[t-1] + theta * eps[t-1] + eps[t]
    where r[t] = log(price[t] / price[t-1])

- **Estimation:** Gaussian conditional maximum likelihood via
  `scipy.optimize.minimize` (L-BFGS-B with bounded parameters).
- **Rolling window:** 90 observations.
- **Forecast:** one-step-ahead.
- **Reconstruction:** `price_hat[t] = price[t-1] * exp(r_hat[t])`.

For every index `t` in `[window, n)`, the model is refit on
`returns[t-window : t]`. The projected series therefore adapts to
local dynamics.

### Divergence

    d[t] = price_observed[t] - price_projected[t]

### Z-score

    z[t] = (d[t] - mean(d[t-window:t])) / std(d[t-window:t])

Warm-up: `None` for the first 20 observations (insufficient sample).
Zero variance: `None` (avoids NaN/inf).

### Interpretation thresholds

| |z|        | Label        |
| --------- | ------------ |
| < 1.0     | `normal`     |
| 1.0 – 2.0 | `notable`    |
| 2.0 – 3.0 | `extreme`    |
| >= 3.0    | `persistent` |

## Empirical validation (2026-09-15)

Same window (90d), same period (1y), same source (Yahoo):

| Pair    | Regime       | current_zscore | interpretation |
| ------- | ------------ | -------------- | -------------- |
| USD/CHF | `free_float` | **+0.55**      | `normal`       |
| USD/BOB | `unknown`    | **-2.43**      | `extreme`      |

The indicator discriminates between a clean-float pair and an
intervened pair **without using any fundamental data**. The USD/BOB
reading is consistent with the ongoing BCB intervention in the
Bolivian FX market.

## Files

- `backend/src/meridian_fx/decision/divergence/arima.py` — projector
- `backend/src/meridian_fx/decision/divergence/metrics.py` — z-score
- `backend/src/meridian_fx/decision/divergence/report.py` — report
- `backend/layer1/routers/divergence.py` — HTTP endpoint
- `backend/tests/test_divergence.py` — 10 tests

## Endpoint

    GET /v1/fx/{pair}/regime-divergence?window_days=90&period=1y

Response includes:

- `observed_series`: [[date, price], ...]
- `projected_series`: [[date, price_hat], ...]
- `divergence_series`: [[date, z], ...]
- `current_zscore`: float | null
- `interpretation`: normal | notable | extreme | persistent | unavailable

## Limitations

1. **Yahoo data quality for illiquid pairs.** The USD/BOB series from
   Yahoo does not reflect the real market rate. The divergence measures
   the statistical anomaly in that series, not in the true market
   price. This is a data-source limitation, not a method limitation.
2. **No causality.** A high z-score is consistent with intervention,
   but does not prove it. Other explanations (structural break,
   liquidity event, data error) are possible.
3. **Warm-up.** The first 90 observations produce no projection; the
   first 20 divergence observations produce no z-score.
4. **Single-model baseline.** The "clean float" baseline is a single
   ARIMA(1,0,1). Other baselines (VAR, cointegration, PPP) are not
   implemented.

## Not used

- `backend/layer3/models/arima.py` — historical, broken (imports
  `statsmodels`, not installed). Deliberately left untouched.

## Future (v3.0)

- Fundamental features (reserves, monetary base, fiscal balance) to
  compare against the ARIMA baseline.
- PPP reference as an alternative baseline.
- Combined indicator (ARIMA + PPP).
