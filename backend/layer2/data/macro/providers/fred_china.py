"""
FRED China Provider - Datos macro de China via FRED API (PRIMARY).

FRED es el proveedor primario.
La simulación de datos está DESACTIVADA para este provider.
Si FRED no proporciona datos reales, available=False.
"""

import logging
from datetime import datetime
from typing import Optional

from backend.layer2.data.sources.fred import FredDataSource
from .base import CountryMacroContext, CountryMacroProvider

logger = logging.getLogger(__name__)


class FREDChinaProvider(CountryMacroProvider):
    """
    Proveedor de datos macro de China via FRED API (PRIMARY).
    
    NO utiliza datos simulados. Si FRED no responde, available=False.
    """

    def __init__(self, api_key: Optional[str] = None):
        # allow_simulation=False -> NO datos simulados
        self._source = FredDataSource(api_key, allow_simulation=False)
        self._cache: Optional[CountryMacroContext] = None

    @property
    def currency(self) -> str:
        return "CNY"

    @property
    def source(self) -> str:
        return "FRED"

    async def get_context(self, force_refresh: bool = False) -> CountryMacroContext:
        """Obtiene el contexto macro de China via FRED (sin simulación)."""
        if not force_refresh and self._cache:
            return self._cache

        try:
            # Series FRED para China
            gdp_data = await self._source.fetch_series("CHNGDP", limit=5)
            cpi_data = await self._source.fetch_series("CHNCPIALL", limit=5)
            unemp_data = await self._source.fetch_series("CHNUR", limit=5)

            gdp_growth = None
            inflation = None
            unemployment = None

            # Verificar que los datos no sean simulados
            if gdp_data and gdp_data.get("observations") and gdp_data.get("available", True):
                obs = gdp_data["observations"]
                if len(obs) >= 2:
                    current = obs[0]["value"]
                    previous = obs[1]["value"]
                    if current and previous and previous != 0:
                        gdp_growth = round(((current - previous) / previous) * 100, 2)

            if cpi_data and cpi_data.get("observations") and cpi_data.get("available", True):
                obs = cpi_data["observations"]
                if len(obs) >= 2:
                    current = obs[0]["value"]
                    previous = obs[1]["value"]
                    if current and previous and previous != 0:
                        inflation = round(((current - previous) / previous) * 100, 2)

            if unemp_data and unemp_data.get("observations") and unemp_data.get("available", True):
                obs = unemp_data["observations"]
                if obs and obs[0].get("value"):
                    unemployment = float(obs[0]["value"])

            # NO tenemos policy_rate de FRED para China
            policy_rate = None

            available = (gdp_growth is not None) or (inflation is not None) or (unemployment is not None)

            context = CountryMacroContext(
                currency="CNY",
                policy_rate=policy_rate,
                gdp_growth=gdp_growth,
                inflation=inflation,
                unemployment=unemployment,
                timestamp=datetime.now(),
                source="FRED",
                available=available,
                is_fallback=not available,
                reason="Datos reales de FRED para China" if available else "FRED no tiene datos disponibles para China",
            )

            self._cache = context
            return context

        except Exception as e:
            logger.error(f"Error fetching FRED China data: {e}")
            return CountryMacroContext(
                currency="CNY",
                available=False,
                is_fallback=True,
                reason=f"FRED China error: {str(e)}",
                timestamp=datetime.now(),
                source="FRED",
            )
