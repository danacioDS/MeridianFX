"""
CNBS/NBS Provider - Datos macro de China via National Bureau of Statistics.

Fuente oficial: https://data.stats.gov.cn/
Endpoint: https://data.stats.gov.cn/easyquery.htm

Indicadores disponibles:
- GDP Growth (trimestral)
- CPI Inflation (mensual)
- Unemployment Rate (mensual)
- Industrial Production (mensual)

Este provider NO genera datos simulados. Si la API no responde o no
entrega datos válidos, available=False.

⚠️  INCOMPLETE — see KNOWN_ISSUES.md KI-008.
    The NBS API call and response parser are scaffolded but not
    implemented. This provider currently returns available=False
    unconditionally. It IS wired into ChainCNYProvider and the chain
    falls through to World Bank when this provider is unavailable.
"""

import logging
import httpx
from datetime import datetime
from typing import Optional, Dict, Any

from .base import CountryMacroContext, CountryMacroProvider

logger = logging.getLogger(__name__)


class CNBSProvider(CountryMacroProvider):
    """
    Proveedor de datos macro de China via NBS (National Bureau of Statistics).
    
    Fuente oficial china. Datos en tiempo real.
    """

    def __init__(self):
        self._cache: Optional[CountryMacroContext] = None
        self._base_url = "https://data.stats.gov.cn/easyquery.htm"

    @property
    def currency(self) -> str:
        return "CNY"

    @property
    def source(self) -> str:
        return "CNBS/NBS"

    async def get_context(self, force_refresh: bool = False) -> CountryMacroContext:
        """Obtiene el contexto macro de China via NBS."""
        if not force_refresh and self._cache:
            return self._cache

        try:
            data = await self._fetch_nbs_data()
            if data:
                context = self._parse_nbs_response(data)
                self._cache = context
                return context
        except Exception as e:
            logger.error(f"Error fetching CNBS data: {e}")

        # Si falla, devolver unavailable (sin datos inventados)
        context = CountryMacroContext(
            currency="CNY",
            available=False,
            is_fallback=True,
            reason="CNBS/NBS API no disponible o datos no encontrados",
            timestamp=datetime.now(),
            source=self.source,
        )
        self._cache = context
        return context

    async def _fetch_nbs_data(self) -> Optional[Dict[str, Any]]:
        """Obtiene datos de la API de NBS.

        INCOMPLETE — see KNOWN_ISSUES.md KI-008.

        The NBS response structure is not yet mapped (`_parse_nbs_response`
        returns a hard-coded unavailable context). To avoid an unnecessary
        network call whose result would be discarded, this method returns
        None until both the API call and the parser are implemented.
        """
        # TODO(KI-008): implement NBS API call + response parser.
        return None

    def _parse_nbs_response(self, data: Dict[str, Any]) -> CountryMacroContext:
        """Parsea la respuesta de NBS."""
        # TODO: Implementar parsing específico según estructura de NBS
        # Por ahora, devolvemos unavailable hasta tener la estructura exacta
        return CountryMacroContext(
            currency="CNY",
            available=False,
            is_fallback=True,
            reason="CNBS/NBS parsing pendiente - estructura de datos por definir",
            timestamp=datetime.now(),
            source=self.source,
        )
