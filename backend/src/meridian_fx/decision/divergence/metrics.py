"""Rolling z-score on observed vs projected divergence."""
from __future__ import annotations

import math


def rolling_zscore(
    observed: list[float],
    projected: list[float],
    window: int = 90,
    warmup: int = 20,
) -> list[float | None]:
    """Compute rolling z-score of (observed - projected) divergence.

    z[t] = (d[t] - mean(d[t-window:t])) / std(d[t-window:t])

    Returns None for indices where:
      - fewer than `warmup` observations are available, or
      - the rolling standard deviation is zero (no divergence yet).
    """
    n = len(observed)
    if len(projected) != n:
        raise ValueError("observed and projected must have the same length")

    divergences = [o - p for o, p in zip(observed, projected)]
    z_scores: list[float | None] = []

    for i in range(n):
        start = max(0, i - window)
        win = divergences[start:i + 1]
        if len(win) < warmup:
            z_scores.append(None)
            continue
        mu = sum(win) / len(win)
        var = sum((x - mu) ** 2 for x in win) / len(win)
        sigma = math.sqrt(var)
        if sigma <= 0.0:
            z_scores.append(None)
            continue
        z_scores.append((divergences[i] - mu) / sigma)

    return z_scores
