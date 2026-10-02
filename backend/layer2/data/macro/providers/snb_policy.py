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
import pandas as pd

from .policy_rate import PolicyRateProvider, PolicyRateResult
from .base import CountryMacroContext

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


    async def get_historical(
        self,
        start_date: str,
        end_date: str,
    ) -> "pd.DataFrame":
        """
        Histórico de la policy rate oficial del SNB.

        Fuente: SNB Data Portal, cube snboffzisa, serie LZ.
        Frecuencia mensual. Columnas: ['date', 'policy_rate'].
        """
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                r = await client.get(self._base_url)
                r.raise_for_status()
                payload = r.json()

            values = payload["timeseries"][0]["values"]
            rows = [
                {
                    "date": pd.to_datetime(v["date"], format="%Y-%m"),
                    "policy_rate": float(v["value"]),
                }
                for v in values
                if v.get("value") is not None
            ]
            df = pd.DataFrame(rows)
            if df.empty:
                return pd.DataFrame(columns=["date", "policy_rate"])

            # El cube snboffzisa{LZ} publica 0.0 en los meses en que no
            # ha actualizado. Cortar la serie en el último valor no-cero
            # evita calcular policy_diff sobre datos espurios.
            last_nonzero = df[df["policy_rate"] != 0.0].index.max()
            if pd.notna(last_nonzero):
                df = df.loc[:last_nonzero].copy()

            mask = (
                (df["date"] >= pd.to_datetime(start_date))
                & (df["date"] <= pd.to_datetime(end_date))
            )
            return (
                df.loc[mask]
                .drop_duplicates(subset=["date"])
                .sort_values("date")
                .reset_index(drop=True)
            )
        except Exception as e:
            logger.error(f"SNB historical error: {e}")
            return pd.DataFrame(columns=["date", "policy_rate"])


    async def get_context(self, force_refresh: bool = False) -> CountryMacroContext:
        """Contexto macro de Suiza. Solo policy_rate tiene fuente oficial aquí."""
        result = await self.get_policy_rate()

        # El cube snboffzisa{LZ} tiene los últimos meses en 0.0 (serie
        # desactualizada). Un 0.0 espurio produce un policy_diff falso.
        # Se marca available=False para que el pipeline impute por mediana.
        if result.available and result.rate == 0.0:
            return CountryMacroContext(
                currency="CHF",
                policy_rate=None,
                timestamp=result.timestamp,
                source="SNB Official API",
                available=False,
                reason="SNB LZ series stale (trailing zeros)",
            )

        return CountryMacroContext(
            currency="CHF",
            policy_rate=result.rate if result.available else None,
            timestamp=result.timestamp,
            source="SNB Official API",
            available=result.available,
            reason=result.reason,
        )
