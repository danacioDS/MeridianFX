"""
Banxico Provider - Tasa objetivo oficial de México.

Fuente: Banco de México API (SIE)
API: https://www.banxico.org.mx/SieAPIRest/
Serie: SF61745 - Tasa objetivo (target rate)

Requisitos:
- TLS 1.3 (a partir del 23 de marzo de 2023)
- Formato de fecha: DD/MM/YYYY
"""

import logging
import os
from dotenv import load_dotenv
load_dotenv()
import pandas as pd
import httpx
from datetime import datetime
from typing import Optional

from .base import CountryMacroContext, CountryMacroProvider

logger = logging.getLogger(__name__)


class BanxicoProvider(CountryMacroProvider):
    """Proveedor de datos macro de México via Banxico API."""

    def __init__(self):
        self._cache: Optional[CountryMacroContext] = None
        self._base_url = "https://www.banxico.org.mx/SieAPIRest/service/v1/series/SF61745"
        self._token = os.environ.get("BANXICO_TOKEN")

    @property
    def currency(self) -> str:
        return "MXN"

    @property
    def source(self) -> str:
        return "Banxico Official API"

    async def get_historical(
        self,
        start_date: str,
        end_date: str,
    ) -> pd.DataFrame:
        """Obtiene el histórico de la tasa objetivo de Banxico."""
        if not self._token:
            logger.warning("BANXICO_TOKEN not set; returning empty")
            return pd.DataFrame(columns=["date", "policy_rate"])
        try:
            # Banxico espera formato DD/MM/YYYY
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")

            url = (
                f"{self._base_url}/datos/"
                f"{start_dt.strftime('%Y-%m-%d')}/"
                f"{end_dt.strftime('%Y-%m-%d')}"
            )

            logger.info(f"Banxico request: {url}")

            async with httpx.AsyncClient(
                timeout=15.0,
                http2=False,
                verify=True,
            ) as client:
                response = await client.get(
                    url,
                    headers={"Bmx-Token": self._token},
                )

                if response.status_code != 200:
                    logger.error(
                        "Banxico API error: %s - %s",
                        response.status_code,
                        response.text[:200],
                    )
                    return pd.DataFrame(columns=["date", "policy_rate"])

                data = response.json()

                series_data = data.get("bmx", {}).get("series", [])
                if not series_data:
                    logger.warning("No series data in Banxico response")
                    return pd.DataFrame(columns=["date", "policy_rate"])

                datos = series_data[0].get("datos", [])
                if not datos:
                    logger.warning("No datos in Banxico response")
                    return pd.DataFrame(columns=["date", "policy_rate"])

                rows = []
                for obs in datos:
                    fecha = obs.get("fecha")
                    valor = obs.get("dato")

                    if not fecha or valor in (None, "", ".", "N/E"):
                        continue

                    try:
                        obs_date = datetime.strptime(fecha, "%d/%m/%Y")
                        rows.append({
                            "date": obs_date,
                            "policy_rate": float(valor),
                        })
                    except (ValueError, TypeError) as e:
                        logger.debug(f"Error parsing Banxico observation: {e}")
                        continue

                if not rows:
                    logger.warning("No valid rows parsed from Banxico response")
                    return pd.DataFrame(columns=["date", "policy_rate"])

                df = pd.DataFrame(rows)
                df = (
                    df[["date", "policy_rate"]]
                    .dropna()
                    .drop_duplicates(subset=["date"])
                    .sort_values("date")
                    .reset_index(drop=True)
                )

                logger.info(f"Banxico: {len(df)} observations retrieved")
                return df

        except httpx.ConnectError as e:
            logger.error(f"Banxico connection error (TLS 1.3 required): {e}")
            return pd.DataFrame(columns=["date", "policy_rate"])
        except Exception as e:
            logger.error(f"Error fetching historical Banxico data: {e}")
            return pd.DataFrame(columns=["date", "policy_rate"])

    async def get_context(self, force_refresh: bool = False) -> CountryMacroContext:
        if not force_refresh and self._cache:
            return self._cache

        try:
            from datetime import timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)

            df = await self.get_historical(
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d"),
            )

            policy_rate = df.iloc[-1]["policy_rate"] if not df.empty else None
            available = policy_rate is not None

            context = CountryMacroContext(
                currency="MXN",
                policy_rate=policy_rate,
                gdp_growth=None,
                inflation=None,
                unemployment=None,
                timestamp=datetime.now(),
                source=self.source,
                available=available,
                is_fallback=False,
                reason="Tasa objetivo oficial de Banxico (SF43718)" if available else "No disponible",
            )

            self._cache = context
            return context

        except Exception as e:
            logger.error(f"Error fetching Banxico context: {e}")
            return CountryMacroContext(
                currency="MXN",
                available=False,
                is_fallback=True,
                reason=f"Banxico API error: {str(e)}",
                timestamp=datetime.now(),
                source=self.source,
            )
