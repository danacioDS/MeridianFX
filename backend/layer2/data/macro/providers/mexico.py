"""
Mexico Provider - Datos macro de México via FRED.

Series FRED:
- IRLTLT01MXM156N: Long-term interest rates (proxy para policy_rate)
"""

import logging
from datetime import datetime
from typing import Optional

from backend.layer2.data.sources.fred import FredDataSource
from .base import CountryMacroContext, CountryMacroProvider

logger = logging.getLogger(__name__)


class MexicoProvider(CountryMacroProvider):
    """Proveedor de datos macro de México via FRED."""

    def __init__(self, api_key: Optional[str] = None):
        self._source = FredDataSource(api_key, allow_simulation=False)
        self._cache: Optional[CountryMacroContext] = None

    @property
    def currency(self) -> str:
        return "MXN"

    @property
    def source(self) -> str:
        return "FRED (Mexico)"

    async def get_context(self, force_refresh: bool = False) -> CountryMacroContext:
        if not force_refresh and self._cache:
            return self._cache

        try:
            rate_data = await self._source.fetch_series("IRLTLT01MXM156N", limit=2)
            policy_rate = None

            if rate_data and rate_data.get("observations"):
                obs = rate_data["observations"]
                if obs and obs[0].get("value"):
                    policy_rate = float(obs[0]["value"])

            available = policy_rate is not None

            context = CountryMacroContext(
                currency="MXN",
                policy_rate=policy_rate,
                gdp_growth=None,
                inflation=None,
                unemployment=None,
                timestamp=datetime.now(),
                source="FRED (Mexico)",
                available=available,
                is_fallback=not available,
                reason="Long-term rates como policy_rate para Mexico" if available else "FRED Mexico no disponible",
            )

            self._cache = context
            return context

        except Exception as e:
            logger.error(f"Error fetching Mexico data: {e}")
            return CountryMacroContext(
                currency="MXN",
                available=False,
                is_fallback=True,
                reason=f"FRED Mexico error: {str(e)}",
                timestamp=datetime.now(),
                source="FRED",
            )
