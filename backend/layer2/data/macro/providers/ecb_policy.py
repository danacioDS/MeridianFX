"""
ECB Policy Rate Provider - Euro Area.

Fuente: ECB Official API (SDMX)
Serie: FM.D.U2.EUR.4F.KR.DFR.LEV (Deposit Facility Rate)

API: https://data-api.ecb.europa.eu/service/data/FM/D.U2.EUR.4F.KR.DFR.LEV
"""

import logging
import httpx
from datetime import datetime
from typing import Optional

from .policy_rate import PolicyRateProvider, PolicyRateResult

logger = logging.getLogger(__name__)


class ECBPolicyRateProvider(PolicyRateProvider):
    """
    Proveedor de policy rate para Euro Area (EUR).
    
    Obtiene la Deposit Facility Rate del ECB via API oficial.
    """

    def __init__(self):
        self._cache: Optional[PolicyRateResult] = None
        self._base_url = "https://data-api.ecb.europa.eu/service/data/FM/D.U2.EUR.4F.KR.DFR.LEV"

    @property
    def currency(self) -> str:
        return "EUR"

    async def get_historical(
        self,
        start_date: str,
        end_date: str,
    ):
        """
        Obtiene el histórico real de la Deposit Facility Rate (DFR).

        Fuente oficial:
        FM.D.U2.EUR.4F.KR.DFR.LEV

        Conserva la fecha de observación del ECB.
        """
        import pandas as pd
        import csv
        from io import StringIO

        try:
            params = {
                "format": "csvdata",
                "startPeriod": start_date,
                "endPeriod": end_date,
            }

            headers = {
                "Accept": "text/csv",
            }

            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    self._base_url,
                    params=params,
                    headers=headers,
                )

            if response.status_code != 200:
                logger.error(
                    "ECB historical API error: %s",
                    response.status_code,
                )
                return pd.DataFrame(columns=["date", "policy_rate"])

            reader = csv.DictReader(
                StringIO(response.text)
            )

            rows = []

            for row in reader:
                date_value = row.get("TIME_PERIOD")
                rate_value = row.get("OBS_VALUE")

                if not date_value or rate_value in (None, "", "."):
                    continue

                try:
                    rows.append({
                        "date": pd.to_datetime(date_value),
                        "policy_rate": float(rate_value),
                    })
                except (ValueError, TypeError):
                    continue

            if not rows:
                logger.warning(
                    "No historical ECB DFR observations for %s -> %s",
                    start_date,
                    end_date,
                )
                return pd.DataFrame(columns=["date", "policy_rate"])

            df = pd.DataFrame(rows)

            df = (
                df[["date", "policy_rate"]]
                .dropna()
                .drop_duplicates(subset=["date"])
                .sort_values("date")
                .reset_index(drop=True)
            )

            return df

        except Exception as e:
            logger.error(
                "Error fetching historical ECB DFR: %s",
                e,
            )
            return pd.DataFrame(columns=["date", "policy_rate"])

    async def get_policy_rate(self) -> PolicyRateResult:
        if self._cache:
            return self._cache

        try:
            rate = await self._fetch_ecb_rate()
            if rate is not None:
                result = PolicyRateResult(
                    currency="EUR",
                    rate=rate,
                    source="ECB Official API",
                    timestamp=datetime.now(),
                    available=True,
                    reason="ECB Deposit Facility Rate (DFR)",
                )
                self._cache = result
                return result
        except Exception as e:
            logger.error(f"ECB API error: {e}")

        result = PolicyRateResult(
            currency="EUR",
            rate=None,
            source="ECB Official API",
            timestamp=datetime.now(),
            available=False,
            reason="ECB API unavailable",
        )
        self._cache = result
        return result

    async def _fetch_ecb_rate(self) -> Optional[float]:
        """Obtiene la Deposit Facility Rate desde la API del ECB."""
        try:
            params = {
                "format": "csvdata",
                "startPeriod": "2026-01-01",
            }
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(self._base_url, params=params)
                
                if response.status_code != 200:
                    logger.error(f"ECB API error: {response.status_code}")
                    return None
                
                # Parsear CSV
                lines = response.text.strip().split('\n')
                if len(lines) < 2:
                    return None
                
                # Última línea tiene el valor más reciente
                last_line = lines[-1]
                parts = last_line.split(',')
                
                # El valor está en la posición 9 (OBS_VALUE)
                if len(parts) > 9:
                    try:
                        return float(parts[9])
                    except (ValueError, IndexError):
                        pass
                return None
                
        except Exception as e:
            logger.error(f"Error fetching ECB rate: {e}")
            return None
