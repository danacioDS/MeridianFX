"""Layer 2 v3.4.1 §7.2 — Dynamic transaction costs.

ALL units are BASIS POINTS (bps).

    normalized_volatility = (VIX - 10) / (30 - 10), clipped to [0, 1]
    spread  = base_min + (base_max - base_min) x normalized_volatility
    slippage = base_slippage(category) x (VIX / 20)
    commission = 0.5 (fixed per trade)
    total_cost = spread + slippage + commission

Patch P2 (prompt v1.1):
  * VIX MUST be retrieved from Layer 4 FeatureStore.get_feature('vix', T).
  * If VIX is unavailable → signal = UNAVAILABLE.
  * DO NOT implement an alternative VIX acquisition path.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from ..contracts.providers import FeatureStore

VIX_FEATURE_ID = "vix"
VIX_FLOOR = 10.0
VIX_CEIL = 30.0
COMMISSION_BPS = 0.5


class VixUnavailableError(RuntimeError):
    """VIX missing → signal UNAVAILABLE (Patch P2)."""


class PairCategory(StrEnum):
    MAJOR = "Major"
    MINOR = "Minor"
    EMERGING = "Emerging"
    FRONTIER = "Frontier"


#: Category catalog (L2 §7.2): pairs, base spread range, base slippage.
CATEGORY_CATALOG: dict[PairCategory, dict] = {
    PairCategory.MAJOR: {
        "pairs": ("USDJPY", "EURUSD"),
        "base_min": 0.2,
        "base_max": 0.5,
        "base_slippage": 0.5,
    },
    PairCategory.MINOR: {
        "pairs": ("GBPUSD", "USDCNY"),
        "base_min": 0.3,
        "base_max": 0.6,
        "base_slippage": 1.0,
    },
    PairCategory.EMERGING: {
        "pairs": ("USDMXN", "USDBRL"),
        "base_min": 1.0,
        "base_max": 2.0,
        "base_slippage": 2.0,
    },
    PairCategory.FRONTIER: {
        "pairs": ("USDARS", "USDBOB"),
        "base_min": 3.0,
        "base_max": 5.0,
        "base_slippage": 3.0,
    },
}

_PAIR_TO_CATEGORY: dict[str, PairCategory] = {
    pair: category
    for category, meta in CATEGORY_CATALOG.items()
    for pair in meta["pairs"]
}


class CostBreakdown(BaseModel):
    """Per-trade cost decomposition in bps (L2 §7.2 / DecisionRecord §13)."""

    model_config = ConfigDict(extra="forbid")

    spread: float
    slippage: float
    commission: float
    total_cost: float
    normalized_volatility: float
    vix: float


class CostCalculator:
    """Computes spread, slippage, commission and total cost (bps).

    VIX is injected from a Layer 4 FeatureStore; there is NO alternative path
    (Patch P2). ``None`` VIX raises VixUnavailableError → signal UNAVAILABLE.
    """

    @staticmethod
    def category_for(pair: str) -> PairCategory:
        try:
            return _PAIR_TO_CATEGORY[pair]
        except KeyError as exc:
            raise ValueError(f"pair {pair!r} not present in cost catalog") from exc

    @staticmethod
    def normalized_volatility(vix: float) -> float:
        """Linear VIX interpolation (not percentile) clipped to [0, 1]."""
        return max(0.0, min(1.0, (vix - VIX_FLOOR) / (VIX_CEIL - VIX_FLOOR)))

    @staticmethod
    def vix_from_feature_store(
        pair: str, store: FeatureStore, as_of, vix_feature_id: str = VIX_FEATURE_ID
    ) -> float:
        """Retrieve VIX from Layer 4 FeatureStore (Patch P2).

        Raises VixUnavailableError when the feature is missing so the signal
        is marked UNAVAILABLE — no fallback logic is permitted.
        """
        value = store.get_feature(vix_feature_id, as_of)
        if value is None or value.value is None:
            raise VixUnavailableError(
                f"VIX unavailable from FeatureStore at {as_of} → signal UNAVAILABLE"
            )
        return float(value.value)

    @staticmethod
    def calculate_total_cost(pair: str, vix: float) -> CostBreakdown:
        """total_cost = spread + slippage + commission  (L2 §7.2)."""
        if vix is None:
            raise VixUnavailableError("VIX missing → signal UNAVAILABLE (Patch P2)")
        meta = CATEGORY_CATALOG[CostCalculator.category_for(pair)]
        norm = CostCalculator.normalized_volatility(vix)
        spread = meta["base_min"] + (meta["base_max"] - meta["base_min"]) * norm
        slippage = meta["base_slippage"] * (vix / 20.0)
        commission = COMMISSION_BPS
        total = spread + slippage + commission
        return CostBreakdown(
            spread=round(spread, 6),
            slippage=round(slippage, 6),
            commission=commission,
            total_cost=round(total, 6),
            normalized_volatility=round(norm, 6),
            vix=vix,
        )