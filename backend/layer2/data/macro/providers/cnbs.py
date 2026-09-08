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
        """Obtiene datos de la API de NBS."""
        try:
            # Parámetros para obtener datos económicos de China
            params = {
                "m": "QueryData",
                "dbcode": "hgyd",
                "rowcode": "reg",
                "colcode": "sj",
                "wds": "[]",
                "dfwds": '[]',
            }
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(self._base_url, params=params)
                if response.status_code == 200:
                    return response.json()
                logger.warning(f"NBS API error: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"NBS request failed: {e}")
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
