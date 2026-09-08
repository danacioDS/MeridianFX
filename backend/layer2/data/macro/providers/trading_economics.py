"""
Trading Economics Provider - Datos macro de países via Trading Economics API.

Fuente: https://tradingeconomics.com/
API: https://tradingeconomics.com/api/

Indicadores disponibles:
- policy_rate: Interest Rate (Loan Prime Rate 1Y)
- gdp_growth: GDP Annual Growth Rate
- inflation: Inflation Rate
- unemployment: Unemployment Rate
- yield_10y: 10-Year Bond Yield
- yield_2y: 2-Year Bond Yield
"""

import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any

import httpx

from .base import CountryMacroContext, CountryMacroProvider

logger = logging.getLogger(__name__)


class TradingEconomicsProvider(CountryMacroProvider):
    """
    Proveedor de datos macro via Trading Economics API.
    
    Requiere API_KEY en entorno TRADING_ECONOMICS_API_KEY.
    Fallback a valores estimados si no hay API key.
    """

    # Mapeo de monedas a códigos de país Trading Economics
    COUNTRY_MAP = {
        "CNY": "china",
        "EUR": "euro-area",
        "GBP": "united-kingdom",
        "JPY": "japan",
        "MXN": "mexico",
        "BRL": "brazil",
        "ARS": "argentina",
        "BOB": "bolivia",
        "CHF": "switzerland",
        "USD": "united-states",
    }

    def __init__(self, currency: str, api_key: Optional[str] = None):
        self._currency = currency.upper()
        self._country = self.COUNTRY_MAP.get(self._currency)
        self._api_key = api_key or os.getenv("TRADING_ECONOMICS_API_KEY")
        self._cache: Optional[CountryMacroContext] = None

    @property
    def currency(self) -> str:
        return self._currency

    @property
    def source(self) -> str:
        return "Trading Economics"

    async def get_context(self, force_refresh: bool = False) -> CountryMacroContext:
        """Obtiene el contexto macro del país via Trading Economics API."""
        if not force_refresh and self._cache:
            return self._cache

        if self._country is None:
            return CountryMacroContext(
                currency=self._currency,
                available=False,
                reason=f"No Trading Economics country mapping for {self._currency}",
                timestamp=datetime.now(),
                source=self.source,
            )

        if self._api_key:
            try:
                data = await self._fetch_from_api()
                if data:
                    context = self._parse_api_response(data)
                    self._cache = context
                    return context
            except Exception as e:
                logger.warning(f"Trading Economics API error: {e}")

        # Fallback: estimados desde fuente pública
        return self._fallback_context()

    async def _fetch_from_api(self) -> Optional[Dict[str, Any]]:
        """Obtiene datos desde la API de Trading Economics."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"https://api.tradingeconomics.com/indicators",
                    params={
                        "c": self._country,
                        "format": "json",
                        "apikey": self._api_key,
                    },
                )
                if response.status_code == 200:
                    return response.json()
                logger.warning(f"Trading Economics API error: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Trading Economics API request failed: {e}")
            return None

    def _parse_api_response(self, data: list) -> CountryMacroContext:
        """Parsea la respuesta de la API."""
        context = CountryMacroContext(
            currency=self._currency,
            timestamp=datetime.now(),
            source=self.source,
            available=False,
            is_fallback=False,
        )

        for item in data:
            indicator = item.get("Indicator", {}).get("Name", "").lower()
            value = item.get("Value")

            if "interest rate" in indicator and context.policy_rate is None:
                context.policy_rate = value
            elif "gdp growth rate" in indicator and context.gdp_growth is None:
                context.gdp_growth = value
            elif "inflation rate" in indicator and context.inflation is None:
                context.inflation = value
            elif "unemployment rate" in indicator and context.unemployment is None:
                context.unemployment = value
            elif "government bond yield 10y" in indicator and context.yield_10y is None:
                context.yield_10y = value
            elif "government bond yield 2y" in indicator and context.yield_2y is None:
                context.yield_2y = value

        # Un contexto solo es utilizable para producción si existe
        # al menos la tasa de política monetaria.
        context.available = context.policy_rate is not None

        if not context.available:
            context.reason = (
                "Trading Economics respondió, pero no entregó "
                "un policy_rate utilizable."
            )

        return context

    def _fallback_context(self) -> CountryMacroContext:
        """
        No genera valores económicos artificiales.

        Si Trading Economics no está disponible o no entrega un
        policy_rate utilizable, el provider devuelve explícitamente
        un contexto unavailable.
        """
        return CountryMacroContext(
            currency=self._currency,
            policy_rate=None,
            gdp_growth=None,
            inflation=None,
            unemployment=None,
            timestamp=datetime.now(),
            source=f"{self.source} (unavailable)",
            available=False,
            is_fallback=True,
            reason=(
                "Trading Economics no tiene datos reales disponibles "
                "para este provider."
            ),
        )
