"""
Japan Provider - Datos macro de Japón via FRED.

Series FRED:
- IRLTLT01JPM156N: Long-term interest rates (proxy para policy_rate)
"""

import logging
from datetime import datetime
from typing import Optional

from backend.layer2.data.sources.fred import FredDataSource
from .base import CountryMacroContext, CountryMacroProvider

logger = logging.getLogger(__name__)


class JapanProvider(CountryMacroProvider):
    """Proveedor de datos macro de Japón via FRED."""

    def __init__(self, api_key: Optional[str] = None):
        self._source = FredDataSource(api_key, allow_simulation=False)
        self._cache: Optional[CountryMacroContext] = None

    @property
    def currency(self) -> str:
        return "JPY"

    @property
    def source(self) -> str:
        return "FRED (Japan)"

    async def get_context(self, force_refresh: bool = False) -> CountryMacroContext:
        if not force_refresh and self._cache:
            return self._cache

        try:
            rate_data = await self._source.fetch_series("IRLTLT01JPM156N", limit=2)
            policy_rate = None

            if rate_data and rate_data.get("observations"):
                obs = rate_data["observations"]
                if obs and obs[0].get("value"):
                    policy_rate = float(obs[0]["value"])

            available = policy_rate is not None

            context = CountryMacroContext(
                currency="JPY",
                policy_rate=policy_rate,
                gdp_growth=None,
                inflation=None,
                unemployment=None,
                timestamp=datetime.now(),
                source="FRED (Japan)",
                available=available,
                is_fallback=not available,
                reason="Long-term rates como policy_rate para Japan" if available else "FRED Japan no disponible",
            )

            self._cache = context
            return context

        except Exception as e:
            logger.error(f"Error fetching Japan data: {e}")
            return CountryMacroContext(
                currency="JPY",
                available=False,
                is_fallback=True,
                reason=f"FRED Japan error: {str(e)}",
                timestamp=datetime.now(),
                source="FRED",
            )
