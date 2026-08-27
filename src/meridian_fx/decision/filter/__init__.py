"""Layer 2 economic filter package (Prompt 5).

    * filter/economic.py — §7.1 filter formula (net_return, edge_ratio)
    * filter/costs.py    — §7.2 dynamic transaction costs (VIX from L4, Patch P2)
"""

from .costs import (
    CATEGORY_CATALOG,
    COMMISSION_BPS,
    CostBreakdown,
    CostCalculator,
    PairCategory,
    VixUnavailableError,
)
from .economic import (
    EconomicFilter,
    EconomicFilterResult,
    EdgeThresholdInvalidError,
)

__all__ = [
    "CostCalculator",
    "CostBreakdown",
    "PairCategory",
    "CATEGORY_CATALOG",
    "COMMISSION_BPS",
    "VixUnavailableError",
    "EconomicFilter",
    "EconomicFilterResult",
    "EdgeThresholdInvalidError",
]