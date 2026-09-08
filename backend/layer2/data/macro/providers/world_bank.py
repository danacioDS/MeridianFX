"""
World Bank Provider - Datos macro de China via World Bank API.

Fuente oficial: https://data.worldbank.org/
API: https://api.worldbank.org/v2/

Indicadores disponibles:
- NY.GDP.MKTP.KD.ZG: GDP Growth (%)
- FP.CPI.TOTL.ZG: Inflation (%)
- SL.UEM.TOTL.ZS: Unemployment (%)
- AG.LND.ARBL.ZS: Agricultural Land (%)

Este provider NO genera datos simulados. Si la API no responde,
available=False.
"""

import logging
import httpx
from datetime import datetime
from typing import Optional, Dict, Any

from .base import CountryMacroContext, CountryMacroProvider

logger = logging.getLogger(__name__)


class WorldBankProvider(CountryMacroProvider):
    """
    Proveedor de datos macro de China via World Bank API.
    
    Fuente gratuita, sin API key requerida.
    """

    # Mapeo de indicadores World Bank
    INDICATORS = {
        "gdp_growth": "NY.GDP.MKTP.KD.ZG",
        "inflation": "FP.CPI.TOTL.ZG",
        "unemployment": "SL.UEM.TOTL.ZS",
        "policy_rate": None,  # No disponible en World Bank
    }

    def __init__(self, currency: str = "CN"):
        self._cache: Optional[CountryMacroContext] = None
        self._base_url = f"https://api.worldbank.org/v2/country/{currency.upper()}/indicator"
        self._currency = currency.upper()

    @property
    def currency(self) -> str:
        # World Bank usa códigos de país (CN, EMU, etc.)
        # Mapeamos a moneda para compatibilidad
        currency_map = {
            "CN": "CNY",
            "EMU": "EUR",
            "GB": "GBP",
            "JP": "JPY",
            "MX": "MXN",
            "BR": "BRL",
            "AR": "ARS",
            "BO": "BOB",
            "CH": "CHF",
            "US": "USD",
        }
        return currency_map.get(self._currency, self._currency)

    @property
    def source(self) -> str:
        return "World Bank"

    async def get_context(self, force_refresh: bool = False) -> CountryMacroContext:
        """Obtiene el contexto macro de China via World Bank."""
        if not force_refresh and self._cache:
            return self._cache

        try:
            data = await self._fetch_worldbank_data()
            if data:
                context = self._parse_worldbank_response(data)
                self._cache = context
                return context
        except Exception as e:
            logger.error(f"Error fetching World Bank data: {e}")

        # Si falla, devolver unavailable
        context = CountryMacroContext(
            currency="CNY",
            available=False,
            is_fallback=True,
            reason="World Bank API no disponible",
            timestamp=datetime.now(),
            source=self.source,
        )
        self._cache = context
        return context

    async def _fetch_worldbank_data(self) -> Optional[Dict[str, Any]]:
        """Obtiene datos de la API de World Bank."""
        try:
            results = {}
            async with httpx.AsyncClient(timeout=15.0) as client:
                for key, indicator_id in self.INDICATORS.items():
                    if indicator_id is None:
                        continue
                    
                    url = f"{self._base_url}/{indicator_id}"
                    params = {
                        "format": "json",
                        "per_page": 5,
                        "mrv": 1,  # Most recent value
                    }
                    
                    response = await client.get(url, params=params)
                    if response.status_code == 200:
                        data = response.json()
                        if data and len(data) > 1 and data[1]:
                            results[key] = data[1][0].get("value")
                    else:
                        logger.warning(f"World Bank API error: {response.status_code}")
            
            if results:
                results["available"] = True
                return results
            return None
        except Exception as e:
            logger.error(f"World Bank request failed: {e}")
            return None

    def _parse_worldbank_response(self, data: Dict[str, Any]) -> CountryMacroContext:
        """Parsea la respuesta de World Bank."""
        return CountryMacroContext(
            currency="CNY",
            policy_rate=None,  # No disponible en World Bank
            gdp_growth=data.get("gdp_growth"),
            inflation=data.get("inflation"),
            unemployment=data.get("unemployment"),
            timestamp=datetime.now(),
            source=self.source,
            available=data.get("available", False),
            is_fallback=False,
            reason="Datos de World Bank" if data.get("available") else "Datos no disponibles",
        )
