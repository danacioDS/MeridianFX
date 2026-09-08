"""
SOFR Provider - Tasa de política monetaria de EE.UU. via FRED.

SOFR (Secured Overnight Financing Rate) es la tasa de referencia de la Fed.
Fuente: FRED (o Refinitiv via FRED)

Serie: USDSOFR
"""

import logging
from datetime import datetime
from typing import Optional

from backend.layer2.data.sources.fred import FredDataSource
from .base import CountryMacroContext, CountryMacroProvider

logger = logging.getLogger(__name__)


class SOFRProvider(CountryMacroProvider):
    """
    Proveedor de SOFR como policy_rate para EE.UU.
    """

    def __init__(self, api_key: Optional[str] = None):
        self._source = FredDataSource(api_key, allow_simulation=False)
        self._cache: Optional[CountryMacroContext] = None

    @property
    def currency(self) -> str:
        return "USD"

    @property
    def source(self) -> str:
        return "FRED (SOFR)"

    async def get_context(self, force_refresh: bool = False) -> CountryMacroContext:
        """Obtiene SOFR como policy_rate."""
        if not force_refresh and self._cache:
            return self._cache

        try:
            # Buscar SOFR en FRED
            data = await self._source.fetch_series("SOFR", limit=2)
            policy_rate = None

            if data and data.get("observations"):
                obs = data["observations"]
                if obs and obs[0].get("value"):
                    policy_rate = float(obs[0]["value"])

            available = policy_rate is not None

            context = CountryMacroContext(
                currency="USD",
                policy_rate=policy_rate,
                gdp_growth=None,  # Ya lo tenemos de FREDProvider
                inflation=None,    # Ya lo tenemos de FREDProvider
                unemployment=None, # Ya lo tenemos de FREDProvider
                timestamp=datetime.now(),
                source="FRED (SOFR)",
                available=available,
                is_fallback=not available,
                reason="SOFR como policy_rate" if available else "SOFR no disponible",
            )

            self._cache = context
            return context

        except Exception as e:
            logger.error(f"Error fetching SOFR: {e}")
            return CountryMacroContext(
                currency="USD",
                available=False,
                is_fallback=True,
                reason=f"SOFR error: {str(e)}",
                timestamp=datetime.now(),
                source="FRED",
            )
