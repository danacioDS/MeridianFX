"""
FRED Provider - Datos macro de Estados Unidos via FRED API.
"""

import logging
from datetime import datetime
from typing import Optional

from backend.layer2.data.sources.fred import FredDataSource
from .base import CountryMacroContext, CountryMacroProvider

logger = logging.getLogger(__name__)


class FREDProvider(CountryMacroProvider):
    """Proveedor de datos macro de EE.UU. via FRED."""

    def __init__(self, api_key: Optional[str] = None):
        self._source = FredDataSource(api_key, allow_simulation=False)
        self._cache: Optional[CountryMacroContext] = None

    @property
    def currency(self) -> str:
        return "USD"

    @property
    def source(self) -> str:
        return "FRED"

    async def get_context(self, force_refresh: bool = False) -> CountryMacroContext:
        """Obtiene el contexto macro de EE.UU."""
        if not force_refresh and self._cache:
            return self._cache

        try:
            raw_data = await self._source.get_macro_context()
            summary = raw_data.get("summary", {})

            context = CountryMacroContext(
                currency="USD",
                policy_rate=summary.get("fed_funds"),
                gdp_growth=summary.get("gdp_growth"),
                inflation=summary.get("inflation"),
                unemployment=summary.get("unemployment"),
                yield_10y=summary.get("yield_10y"),
                yield_2y=summary.get("yield_2y"),
                timestamp=datetime.now(),
                source="FRED",
                available=True,
            )

            self._cache = context
            return context

        except Exception as e:
            logger.error(f"Error fetching FRED data: {e}")
            return CountryMacroContext(
                currency="USD",
                available=False,
                reason=f"FRED error: {str(e)}",
                timestamp=datetime.now(),
                source="FRED",
            )
