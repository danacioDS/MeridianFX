"""Rolling ARIMA(1,0,1) projector.

Model on daily log-returns:
    r[t] = c + phi * r[t-1] + theta * eps[t-1] + eps[t]

Estimation: Gaussian conditional maximum likelihood via scipy.optimize.
Forecast: one-step-ahead, rolling over a fixed-size window.
Reconstruction: price_hat[t] = price[t-1] * exp(r_hat[t])

Dependencies: numpy, scipy (statsmodels is NOT used).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize


@dataclass
class _ARIMA11Fit:
    c: float
    phi: float
    theta: float
    sigma2: float
    last_residual: float


def _conditional_neg_loglik(
    params: np.ndarray,
    returns: np.ndarray,
) -> float:
    """Conditional Gaussian negative log-likelihood for ARMA(1,1)."""
    c, phi, theta, log_sigma2 = params
    sigma2 = np.exp(log_sigma2)

    n = len(returns)
    if n < 2:
        return np.inf

    # Reconstruct residuals recursively assuming eps[0] = 0.
    eps = np.zeros(n)
    sse = 0.0
    for t in range(1, n):
        eps_hat = returns[t] - (c + phi * returns[t - 1] + theta * eps[t - 1])
        eps[t] = eps_hat
        sse += eps_hat ** 2

    nll = 0.5 * (n - 1) * np.log(2 * np.pi * sigma2) + 0.5 * sse / sigma2
    if not np.isfinite(nll):
        return np.inf
    return float(nll)


def _fit_arima11(returns: np.ndarray) -> _ARIMA11Fit | None:
    """Fit ARMA(1,1) on returns using scipy.optimize.

    Bounds prevent pathological parameterizations on short windows.
    Returns None if the optimization fails or produces non-finite results.
    """
    if len(returns) < 10:
        return None

    # Initial guess: no AR, no MA, mean only, variance of returns.
    c0 = float(np.mean(returns))
    phi0 = 0.0
    theta0 = 0.0
    log_sigma2_0 = float(np.log(max(np.var(returns), 1e-10)))

    x0 = np.array([c0, phi0, theta0, log_sigma2_0], dtype=float)

    # Bounds: |phi| < 0.99, |theta| < 0.99 to enforce stationarity and
    # invertibility. c is left free. log_sigma2 is bounded to avoid
    # numerical explosion.
    bounds = [
        (None, None),      # c
        (-0.99, 0.99),     # phi
        (-0.99, 0.99),     # theta
        (-30.0, 10.0),     # log_sigma2
    ]

    try:
        res = minimize(
            _conditional_neg_loglik,
            x0,
            args=(returns,),
            method="L-BFGS-B",
            bounds=bounds,
            options={"maxiter": 200, "ftol": 1e-9},
        )
    except Exception:
        return None

    if not res.success or not np.isfinite(res.fun):
        return None

    c, phi, theta, log_sigma2 = res.x
    sigma2 = float(np.exp(log_sigma2))

    # Recompute the last residual for the one-step-ahead forecast.
    n = len(returns)
    eps = np.zeros(n)
    for t in range(1, n):
        eps[t] = returns[t] - (c + phi * returns[t - 1] + theta * eps[t - 1])
    last_residual = float(eps[-1])

    if not all(np.isfinite([c, phi, theta, sigma2, last_residual])):
        return None
    if sigma2 <= 0:
        return None

    return _ARIMA11Fit(
        c=float(c),
        phi=float(phi),
        theta=float(theta),
        sigma2=sigma2,
        last_residual=last_residual,
    )


class RollingARIMAProjector:
    """Rolling one-step-ahead ARIMA(1,0,1) projector on log-returns.

    For each index t in [window, n):
      - Fit ARIMA(1,0,1) on returns[t-window : t]
      - Predict r_hat[t] = c + phi * r[t-1] + theta * eps[t-1]
      - Reconstruct price_hat[t] = price[t-1] * exp(r_hat[t])
    """

    def __init__(self, window: int = 90) -> None:
        if window < 30:
            raise ValueError("window must be >= 30")
        self.window = window

    def project(
        self,
        dates: list[str],
        prices: list[float],
    ) -> tuple[list[tuple[str, float]], list[tuple[str, float]]]:
        """Return (observed_series, projected_series).

        observed_series: [(date, price), ...] — the input series.
        projected_series: [(date, price_hat), ...] — same length as input,
            with the first `window` entries set to the observed price
            (no forecast available yet).

        Alignment is by index: projected_series[i] corresponds to
        dates[i]. The z-score is computed on the residual
        observed[i] - projected[i].
        """
        n = len(prices)
        if n < self.window + 2:
            # Not enough data to project.
            observed = list(zip(dates, prices))
            projected = [(d, p) for d, p in observed]
            return observed, projected

        prices_arr = np.asarray(prices, dtype=float)
        # Guard: prices must be strictly positive for log-returns.
        if not np.all(prices_arr > 0):
            observed = list(zip(dates, prices))
            projected = [(d, p) for d, p in observed]
            return observed, projected

        log_prices = np.log(prices_arr)
        returns = np.diff(log_prices)  # length n - 1

        projected_prices = np.full(n, np.nan, dtype=float)
        # Before window: no projection, echo the observed price.
        for i in range(self.window):
            projected_prices[i] = prices_arr[i]

        for t in range(self.window, n):
            # returns index for t-1 is (t - 1) - 1 = t - 2 because returns
            # is one shorter than prices.
            train_start = t - self.window - 1
            train_end = t - 1  # exclusive
            if train_start < 0:
                train_start = 0
            train = returns[train_start:train_end]
            fit = _fit_arima11(train)
            if fit is None:
                projected_prices[t] = np.nan
                continue
            r_prev = returns[t - 2]
            r_hat = fit.c + fit.phi * r_prev + fit.theta * fit.last_residual
            projected_prices[t] = prices_arr[t - 1] * np.exp(r_hat)

        # Where projection failed, echo the observed price.
        for i in range(n):
            if not np.isfinite(projected_prices[i]):
                projected_prices[i] = prices_arr[i]

        observed = list(zip(dates, prices_arr.tolist()))
        projected = list(zip(dates, projected_prices.tolist()))
        return observed, projected
