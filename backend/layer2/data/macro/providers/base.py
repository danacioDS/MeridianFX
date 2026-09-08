"""
Country Macro Provider - Contrato base para proveedores de datos macro por país.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class CountryMacroContext:
    """
    Contexto macro de un país.
    
    Mantiene compatibilidad con el formato que espera MacroDifferentialProvider
    a través del método to_dict().
    """
    currency: str
    policy_rate: Optional[float] = None      # Tasa de política monetaria (%)
    gdp_growth: Optional[float] = None       # Crecimiento del PIB (%)
    inflation: Optional[float] = None        # Inflación (%)
    unemployment: Optional[float] = None     # Desempleo (%)
    yield_10y: Optional[float] = None        # Rendimiento 10 años (%)
    yield_2y: Optional[float] = None         # Rendimiento 2 años (%)
    timestamp: Optional[datetime] = None
    source: str = "unknown"
    available: bool = False
    reason: Optional[str] = None
    is_fallback: bool = False                # True si son datos estimados/fallback

    def to_dict(self) -> dict:
        """
        Convierte a dict para compatibilidad con MacroDifferentialProvider.
        
        Mantiene la clave 'fed_funds' por compatibilidad con el contrato existente.
        """
        return {
            "summary": {
                "policy_rate": self.policy_rate,
                "fed_funds": self.policy_rate,  # compatibilidad legacy
                "gdp_growth": self.gdp_growth,
                "inflation": self.inflation,
                "unemployment": self.unemployment,
                "yield_10y": self.yield_10y,
                "yield_2y": self.yield_2y,
            }
        }


class CountryMacroProvider(ABC):
    """Proveedor de datos macro para un país."""

    @property
    @abstractmethod
    def currency(self) -> str:
        """Código de la moneda (ej: USD, CNY)."""
        pass

    @property
    @abstractmethod
    def source(self) -> str:
        """Nombre de la fuente de datos."""
        pass

    @abstractmethod
    async def get_context(self, force_refresh: bool = False) -> CountryMacroContext:
        """Obtiene el contexto macro actual del país."""
        pass
