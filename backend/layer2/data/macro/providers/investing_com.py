"""
Investing.com Provider - FALLBACK para datos macro de China.

Este provider utiliza scraping web y por ello se considera una fuente
secundaria. Solo devuelve valores que realmente fueron encontrados.
No utiliza valores económicos hardcodeados.
"""

import logging
import re
from datetime import datetime
from typing import Optional

import httpx
from bs4 import BeautifulSoup

from .base import CountryMacroContext, CountryMacroProvider

logger = logging.getLogger(__name__)


class InvestingComProvider(CountryMacroProvider):
    """Proveedor fallback para China vía Investing.com."""

    def __init__(self):
        self._cache: Optional[CountryMacroContext] = None

    @property
    def currency(self) -> str:
        return "CNY"

    @property
    def source(self) -> str:
        return "Investing.com"

    async def get_context(
        self,
        force_refresh: bool = False,
    ) -> CountryMacroContext:

        if not force_refresh and self._cache:
            return self._cache

        context = await self._fetch_china_data()
        self._cache = context
        return context

    async def _fetch_china_data(self) -> CountryMacroContext:

        policy_rate = None

        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/131.0 Safari/537.36"
                ),
                "Accept": (
                    "text/html,application/xhtml+xml,"
                    "application/xml;q=0.9,*/*;q=0.8"
                ),
                "Accept-Language": "en-US,en;q=0.9",
            }

            url = (
                "https://www.investing.com/"
                "economic-calendar/china-interest-rate-927"
            )

            async with httpx.AsyncClient(
                timeout=15.0,
                follow_redirects=True,
            ) as client:

                response = await client.get(
                    url,
                    headers=headers,
                )

                if response.status_code != 200:
                    return self._unavailable(
                        f"Investing.com HTTP {response.status_code}"
                    )

                soup = BeautifulSoup(
                    response.text,
                    "html.parser",
                )

                value_elem = soup.find(
                    "span",
                    {"data-test": "last-value"},
                )

                if value_elem:
                    match = re.search(
                        r"[-+]?\d+(?:\.\d+)?",
                        value_elem.get_text(strip=True),
                    )

                    if match:
                        policy_rate = float(match.group(0))

            if policy_rate is None:
                return self._unavailable(
                    "Investing.com no devolvió un valor válido"
                )

            return CountryMacroContext(
                currency="CNY",
                policy_rate=policy_rate,
                gdp_growth=None,
                inflation=None,
                unemployment=None,
                timestamp=datetime.now(),
                source="Investing.com",
                available=True,
                is_fallback=True,
                reason=(
                    "Fallback: tasa de política obtenida "
                    "de Investing.com"
                ),
            )

        except Exception as e:
            logger.error(
                "Error fetching Investing.com: %s",
                e,
            )

            return self._unavailable(
                f"Investing.com error: {e}"
            )

    def _unavailable(self, reason: str) -> CountryMacroContext:
        return CountryMacroContext(
            currency="CNY",
            policy_rate=None,
            gdp_growth=None,
            inflation=None,
            unemployment=None,
            timestamp=datetime.now(),
            source="Investing.com",
            available=False,
            is_fallback=True,
            reason=reason,
        )
