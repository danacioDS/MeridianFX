"""
SNB Policy Rate Provider - Suiza.

Fuente: Swiss National Bank (SNB) Official Data Portal.

Cube:
    snboffzisa

Serie:
    LZ - Switzerland - SNB policy rate

API:
    https://data.snb.ch/api/cube/snboffzisa/data/json/en

La serie oficial tiene frecuencia mensual y unidad porcentual.
No se utilizan proxies, tasas de mercado ni valores hardcodeados.
"""

import logging
from datetime import datetime
from typing import Optional, Tuple

import httpx

from .policy_rate import PolicyRateProvider, PolicyRateResult

logger = logging.getLogger(__name__)


class SNBPolicyRateProvider(PolicyRateProvider):
    """
    Proveedor de policy rate para Suiza (CHF).

    Obtiene la tasa oficial del SNB desde su Data Portal.
    """

    def __init__(self):
        self._cache: Optional[PolicyRateResult] = None
        self._base_url = (
            "https://data.snb.ch/api/cube/snboffzisa/data/json/en"
        )

    @property
    def currency(self) -> str:
        return "CHF"

    async def get_policy_rate(self) -> PolicyRateResult:
        if self._cache:
            return self._cache

        try:
            rate, observation_date = await self._fetch_snb_rate()

            if rate is not None:
                result = PolicyRateResult(
                    currency="CHF",
                    rate=rate,
                    source="SNB Official API",
                    timestamp=observation_date,
                    available=True,
                    reason="SNB policy rate (official Data Portal)",
                )

                self._cache = result
                return result

        except Exception as e:
            logger.error(f"SNB API error: {e}")

        result = PolicyRateResult(
            currency="CHF",
            rate=None,
            source="SNB Official API",
            timestamp=datetime.now(),
            available=False,
            reason="SNB official policy rate unavailable",
        )

        self._cache = result
        return result

    async def _fetch_snb_rate(
        self,
    ) -> Tuple[Optional[float], Optional[datetime]]:
        """Obtiene la última observación de la serie oficial LZ."""

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(self._base_url)

            if response.status_code != 200:
                logger.error(
                    f"SNB API error: HTTP {response.status_code}"
                )
                return None, None

            data = response.json()

        for series in data.get("timeseries", []):
            metadata = series.get("metadata", {})
            key = metadata.get("key", "")

            # Serie oficial:
            # EPB@SNB.snboffzisa{LZ}
            if not key.endswith("{LZ}"):
                continue

            values = series.get("values", [])

            if not values:
                return None, None

            # La API devuelve las observaciones en orden cronológico.
            latest = values[-1]

            value = latest.get("value")
            date_str = latest.get("date")

            if value is None or not date_str:
                return None, None

            try:
                observation_date = datetime.strptime(
                    date_str,
                    "%Y-%m",
                )

                return float(value), observation_date

            except (ValueError, TypeError):
                logger.error(
                    f"Invalid SNB observation: "
                    f"date={date_str}, value={value}"
                )
                return None, None

        logger.error("SNB policy rate series {LZ} not found")
        return None, None
