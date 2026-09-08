"""
ECB Provider - Datos macro de la Eurozona via FRED API.

FRED NO tiene datos reales disponibles para la Eurozona.
Este provider devuelve available=False hasta que se conecte una fuente real.
"""

import logging
from datetime import datetime
from typing import Optional

from backend.layer2.data.sources.fred import FredDataSource
from .base import CountryMacroContext, CountryMacroProvider

logger = logging.getLogger(__name__)


class ECBProvider(CountryMacroProvider):
    """
    Proveedor de datos macro de la Eurozona.
    
    Actualmente sin datos reales. available=False hasta que se integre
    una fuente de datos real.
    """

    def __init__(self, api_key: Optional[str] = None):
        self._source = FredDataSource(api_key, allow_simulation=False)
        self._cache: Optional[CountryMacroContext] = None

    @property
    def currency(self) -> str:
        return "EUR"

    @property
    def source(self) -> str:
        return "ECB"

    async def get_context(self, force_refresh: bool = False) -> CountryMacroContext:
        """Obtiene el contexto macro de la Eurozona."""
        if not force_refresh and self._cache:
            return self._cache

        # Sin datos reales por ahora. available=False.
        context = CountryMacroContext(
            currency="EUR",
            available=False,
            is_fallback=True,
            reason="ECB API no integrada. Pendiente conexión con fuente real.",
            timestamp=datetime.now(),
            source="ECB",
        )

        self._cache = context
        return context
