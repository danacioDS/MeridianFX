"""
Bolivia Provider - Datos macro de Bolivia.

Fuentes:
- GDP: World Bank
- Inflation: World Bank
- Unemployment: World Bank
- Policy Rate: No existe oficialmente (se usa encaje legal)

El Banco Central de Bolivia (BCB) no tiene una tasa de política monetaria
tradicional. Se utiliza un sistema de encaje legal.
"""

import logging
import pandas as pd
from datetime import datetime
from typing import Optional

from .world_bank import WorldBankProvider
from .base import CountryMacroContext, CountryMacroProvider

logger = logging.getLogger(__name__)


class BoliviaProvider(CountryMacroProvider):
    """
    Proveedor de datos macro de Bolivia.
    
    Policy rate no está disponible oficialmente.
    """

    def __init__(self):
        self._source = WorldBankProvider("BO")
        self._cache: Optional[CountryMacroContext] = None

    @property
    def currency(self) -> str:
        return "BOB"

    @property
    def source(self) -> str:
        return "World Bank + BCB"


    async def get_historical(
        self,
        start_date: str,
        end_date: str,
    ) -> pd.DataFrame:
        """
        Obtiene el histórico de policy rate para Bolivia.
        
        Nota: Bolivia no tiene una tasa de política monetaria oficial.
        Este método devuelve un DataFrame vacío.
        """
        logger.warning("Bolivia no tiene policy rate histórico disponible")
        return pd.DataFrame(columns=["date", "policy_rate"])
    async def get_context(self, force_refresh: bool = False) -> CountryMacroContext:
        if not force_refresh and self._cache:
            return self._cache

        try:
            # Obtener datos de World Bank
            ctx = await self._source.get_context(force_refresh=force_refresh)
            
            # Policy rate no disponible oficialmente
            context = CountryMacroContext(
                currency="BOB",
                policy_rate=None,
                gdp_growth=ctx.gdp_growth,
                inflation=ctx.inflation,
                unemployment=ctx.unemployment,
                timestamp=datetime.now(),
                source="World Bank + BCB",
                available=ctx.available,
                is_fallback=False,
                reason="Bolivia no tiene una tasa de política monetaria oficial (usa encaje legal)",
            )

            self._cache = context
            return context

        except Exception as e:
            logger.error(f"Error fetching Bolivia data: {e}")
            return CountryMacroContext(
                currency="BOB",
                available=False,
                is_fallback=True,
                reason=f"Error fetching data: {str(e)}",
                timestamp=datetime.now(),
                source="World Bank",
            )
