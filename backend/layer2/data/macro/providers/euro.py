"""
Euro Provider - Datos macro de la Eurozona.

Fuentes:
- GDP: World Bank
- Inflation: World Bank
- Unemployment: World Bank
- Policy Rate: ECB Policy Rate Provider
"""

import logging
from datetime import datetime
from typing import Optional

from .world_bank import WorldBankProvider
from .ecb_policy import ECBPolicyRateProvider
from .base import CountryMacroContext, CountryMacroProvider

logger = logging.getLogger(__name__)


class EuroProvider(CountryMacroProvider):
    """
    Proveedor de datos macro de la Eurozona.
    """

    def __init__(self):
        self._source = WorldBankProvider("EMU")
        self._policy_source = ECBPolicyRateProvider()
        self._cache: Optional[CountryMacroContext] = None

    @property
    def currency(self) -> str:
        return "EUR"

    @property
    def source(self) -> str:
        return "World Bank + ECB"

    async def get_historical(
        self,
        start_date: str,
        end_date: str,
    ):
        """
        Histórico real de policy rate de la Eurozona.

        La tasa de política utilizada es la ECB Deposit Facility Rate.
        """
        return await self._policy_source.get_historical(
            start_date,
            end_date,
        )

    async def get_context(self, force_refresh: bool = False) -> CountryMacroContext:
        if not force_refresh and self._cache:
            return self._cache

        try:
            # Obtener datos de World Bank
            ctx = await self._source.get_context(force_refresh=force_refresh)
            
            # Obtener policy rate
            policy_result = await self._policy_source.get_policy_rate()
            
            context = CountryMacroContext(
                currency="EUR",
                policy_rate=policy_result.rate if policy_result.available else None,
                gdp_growth=ctx.gdp_growth,
                inflation=ctx.inflation,
                unemployment=ctx.unemployment,
                timestamp=datetime.now(),
                source=self.source,
                available=ctx.available and policy_result.available,
                is_fallback=False,
                reason=f"World Bank + ECB: {policy_result.reason}" if policy_result.available else "ECB policy rate no disponible",
            )

            self._cache = context
            return context

        except Exception as e:
            logger.error(f"Error fetching Euro data: {e}")
            return CountryMacroContext(
                currency="EUR",
                available=False,
                is_fallback=True,
                reason=f"Error fetching data: {str(e)}",
                timestamp=datetime.now(),
                source="World Bank",
            )
