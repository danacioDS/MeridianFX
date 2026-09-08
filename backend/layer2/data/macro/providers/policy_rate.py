"""
Policy Rate Provider - Interfaz para obtener policy rates por país.

Principios:
- Cada moneda tiene un proveedor específico
- No se usan datos estimados
- Si no hay datos, return None
- Trazabilidad completa
"""

from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PolicyRateResult:
    """Resultado de policy rate."""
    currency: str
    rate: Optional[float]
    source: str
    timestamp: datetime
    available: bool
    reason: Optional[str] = None


class PolicyRateProvider(ABC):
    """Proveedor de policy rate para un país."""
    
    @property
    @abstractmethod
    def currency(self) -> str:
        pass
    
    @abstractmethod
    async def get_policy_rate(self) -> PolicyRateResult:
        pass
