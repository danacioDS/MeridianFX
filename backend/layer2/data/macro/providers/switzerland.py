"""
Switzerland Provider - Datos macro de Suiza.

Fuentes:
- GDP: World Bank
- Inflation: World Bank
- Unemployment: World Bank
- Policy Rate: SNB Policy Rate Provider
"""

import logging
from datetime import datetime
from typing import Optional

from .world_bank import WorldBankProvider
from .snb_policy import SNBPolicyRateProvider
from .base import CountryMacroContext, CountryMacroProvider

logger = logging.getLogger(__name__)


class SwitzerlandProvider(CountryMacroProvider):
    """
    Proveedor de datos macro de Suiza.
    """

    def __init__(self):
        self._source = WorldBankProvider("CH")
        self._policy_source = SNBPolicyRateProvider()
        self._cache: Optional[CountryMacroContext] = None

    @property
    def currency(self) -> str:
        return "CHF"

    @property
    def source(self) -> str:
        return "World Bank + SNB"

    async def get_context(self, force_refresh: bool = False) -> CountryMacroContext:
        if not force_refresh and self._cache:
            return self._cache

        try:
            # Obtener datos de World Bank
            ctx = await self._source.get_context(force_refresh=force_refresh)
            
            # Obtener policy rate
            policy_result = await self._policy_source.get_policy_rate()
            
            context = CountryMacroContext(
                currency="CHF",
                policy_rate=policy_result.rate if policy_result.available else None,
                gdp_growth=ctx.gdp_growth,
                inflation=ctx.inflation,
                unemployment=ctx.unemployment,
                timestamp=datetime.now(),
                source=self.source,
                available=ctx.available and policy_result.available,
                is_fallback=False,
                reason=f"World Bank + SNB: {policy_result.reason}" if policy_result.available else "SNB policy rate no disponible",
            )

            self._cache = context
            return context

        except Exception as e:
            logger.error(f"Error fetching Switzerland data: {e}")
            return CountryMacroContext(
                currency="CHF",
                available=False,
                is_fallback=True,
                reason=f"Error fetching data: {str(e)}",
                timestamp=datetime.now(),
                source="World Bank",
            )
