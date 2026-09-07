from dataclasses import dataclass
from enum import Enum
from typing import Optional


class MacroDataStatus(Enum):
    """Estado de disponibilidad de datos macro para un par."""
    FULL = "FULL"
    PARTIAL = "PARTIAL"
    UNAVAILABLE = "UNAVAILABLE"
    STALE = "STALE"


@dataclass
class MacroDifferentialStatus:
    """Estado de los diferenciales macro."""
    status: MacroDataStatus
    base_currency: str
    quote_currency: str
    base_available: bool
    quote_available: bool
    reason: Optional[str] = None
    policy_diff_status: str = "UNAVAILABLE"
    growth_diff_status: str = "UNAVAILABLE"
    rate_diff_status: str = "UNAVAILABLE"
    
    def to_dict(self) -> dict:
        return {
            "status": self.status.value,
            "base": self.base_currency,
            "quote": self.quote_currency,
            "base_available": self.base_available,
            "quote_available": self.quote_available,
            "reason": self.reason,
            "policy_diff": self.policy_diff_status,
            "growth_diff": self.growth_diff_status,
            "rate_diff": self.rate_diff_status,
        }
