"""
ECB Provider - Datos macro de la Eurozona via World Bank API.

Datos disponibles:
- GDP Growth: NY.GDP.MKTP.KD.ZG (World Bank)
- Inflation: FP.CPI.TOTL.ZG (World Bank)
- Unemployment: SL.UEM.TOTL.ZS (World Bank)
- Policy Rate: FR.INR.RINR (World Bank - Real Interest Rate)
"""

import logging
from datetime import datetime
from typing import Optional

from .world_bank import WorldBankProvider
from .base import CountryMacroContext, CountryMacroProvider

logger = logging.getLogger(__name__)


class ECBProvider(CountryMacroProvider):
    """
    Proveedor de datos macro de la Eurozona.
    
    Usa World Bank API (sin API key).
    """

    def __init__(self):
        self._source = WorldBankProvider()
        self._cache: Optional[CountryMacroContext] = None

    @property
    def currency(self) -> str:
        return "EUR"

    @property
    def source(self) -> str:
        return "World Bank (ECB)"

    async def get_context(self, force_refresh: bool = False) -> CountryMacroContext:
        """Obtiene el contexto macro de la Eurozona."""
        if not force_refresh and self._cache:
            return self._cache

        try:
            # World Bank no tiene directamente "EUR", usamos "EMU" (Euro Area)
            context = await self._source._fetch_worldbank_data("EMU")
            if context and context.get("available"):
                return CountryMacroContext(
                    currency="EUR",
                    policy_rate=context.get("policy_rate"),
                    gdp_growth=context.get("gdp_growth"),
                    inflation=context.get("inflation"),
                    unemployment=context.get("unemployment"),
                    timestamp=datetime.now(),
                    source="World Bank",
                    available=True,
                    is_fallback=False,
                    reason="Datos de World Bank para Eurozona",
                )
        except Exception as e:
            logger.error(f"Error fetching ECB data: {e}")

        return CountryMacroContext(
            currency="EUR",
            available=False,
            is_fallback=True,
            reason="World Bank no tiene datos disponibles para Eurozona",
            timestamp=datetime.now(),
            source="ECB (unavailable)",
        )
