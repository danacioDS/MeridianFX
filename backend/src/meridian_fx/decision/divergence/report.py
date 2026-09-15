"""Divergence report construction."""
from __future__ import annotations

from dataclasses import dataclass, field

from .arima import RollingARIMAProjector
from .metrics import rolling_zscore


@dataclass
class DivergenceReport:
    """Rolling divergence report for a single pair.

    observed_series and projected_series are aligned by index. The
    residual is `observed - projected`. The z-score is computed on
    that residual over a rolling window.
    """

    pair: str
    regime: str
    window_days: int
    observed_series: list[tuple[str, float]] = field(default_factory=list)
    projected_series: list[tuple[str, float]] = field(default_factory=list)
    divergence_series: list[tuple[str, float | None]] = field(default_factory=list)
    current_zscore: float | None = None
    interpretation: str = "unknown"


def _interpret(z: float | None) -> str:
    if z is None:
        return "unavailable"
    az = abs(z)
    if az < 1.0:
        return "normal"
    if az < 2.0:
        return "notable"
    if az < 3.0:
        return "extreme"
    return "persistent"


def compute_divergence_report(
    pair: str,
    dates: list[str],
    prices: list[float],
    regime: str,
    window: int = 90,
) -> DivergenceReport:
    """Compute the divergence report for a pair.

    Steps:
      1. Project prices using rolling ARIMA(1,0,1).
      2. Compute rolling z-score of observed - projected.
      3. Build the report with aligned series.
    """
    projector = RollingARIMAProjector(window=window)
    observed, projected = projector.project(dates, prices)

    obs_values = [v for _, v in observed]
    proj_values = [v for _, v in projected]

    z_scores = rolling_zscore(obs_values, proj_values, window=window)

    divergence_series = [
        (d, z) for (d, _), z in zip(observed, z_scores)
    ]

    current_z = z_scores[-1] if z_scores else None

    return DivergenceReport(
        pair=pair,
        regime=regime,
        window_days=window,
        observed_series=observed,
        projected_series=projected,
        divergence_series=divergence_series,
        current_zscore=current_z,
        interpretation=_interpret(current_z),
    )
