"""
UK Provider - Datos macro de Reino Unido via FRED.

Series FRED:
- IRLTLT01GBM156N: Long-term interest rates (proxy para policy_rate)
"""

import logging
from datetime import datetime
from typing import Optional

from backend.layer2.data.sources.fred import FredDataSource
from .base import CountryMacroContext, CountryMacroProvider

logger = logging.getLogger(__name__)


class UKProvider(CountryMacroProvider):
    """Proveedor de datos macro de Reino Unido via FRED."""

    def __init__(self, api_key: Optional[str] = None):
        self._source = FredDataSource(api_key, allow_simulation=False)
        self._cache: Optional[CountryMacroContext] = None

    @property
    def currency(self) -> str:
        return "GBP"

    @property
    def source(self) -> str:
        return "FRED (UK)"

    async def get_context(self, force_refresh: bool = False) -> CountryMacroContext:
        if not force_refresh and self._cache:
            return self._cache

        try:
            rate_data = await self._source.fetch_series("IRLTLT01GBM156N", limit=2)
            policy_rate = None

            if rate_data and rate_data.get("observations"):
                obs = rate_data["observations"]
                if obs and obs[0].get("value"):
                    policy_rate = float(obs[0]["value"])

            available = policy_rate is not None

            context = CountryMacroContext(
                currency="GBP",
                policy_rate=policy_rate,
                gdp_growth=None,
                inflation=None,
                unemployment=None,
                timestamp=datetime.now(),
                source="FRED (UK)",
                available=available,
                is_fallback=not available,
                reason="Long-term rates como policy_rate para UK" if available else "FRED UK no disponible",
            )

            self._cache = context
            return context

        except Exception as e:
            logger.error(f"Error fetching UK data: {e}")
            return CountryMacroContext(
                currency="GBP",
                available=False,
                is_fallback=True,
                reason=f"FRED UK error: {str(e)}",
                timestamp=datetime.now(),
                source="FRED",
            )
