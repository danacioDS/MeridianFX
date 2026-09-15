"""Rolling ARIMA(1,0,1) divergence analysis for FX pairs.

Detects when the observed price of a pair diverges from what a
clean-float ARIMA(1,0,1) model would project, rolling one step ahead
over a 90-day window. High persistent divergence is consistent with
central-bank intervention or an administered regime.

This is separate from `layer3/models/arima.py` (which is broken and
imports `statsmodels`, not installed). This module is self-contained,
depends only on numpy and scipy, and is used by the forecast eligibility
gate's supplementary analysis.

See KNOWN_ISSUES.md KI-009 for context.
"""
from .arima import RollingARIMAProjector
from .metrics import rolling_zscore
from .report import DivergenceReport, compute_divergence_report

__all__ = [
    "RollingARIMAProjector",
    "rolling_zscore",
    "DivergenceReport",
    "compute_divergence_report",
]
