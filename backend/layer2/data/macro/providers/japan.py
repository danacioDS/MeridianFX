"""
Japan Provider - Datos macro de Japón via FRED.

Series FRED:
- IRLTLT01JPM156N: Long-term interest rates (proxy para policy_rate)
"""

import logging
import pandas as pd
from datetime import datetime
from typing import Optional

from backend.layer2.data.sources.fred import FredDataSource
from .world_bank import WorldBankProvider
from .base import CountryMacroContext, CountryMacroProvider

logger = logging.getLogger(__name__)


class JapanProvider(CountryMacroProvider):
    """Proveedor de datos macro de Japón via FRED."""

    def __init__(self, api_key: Optional[str] = None):
        self._source = FredDataSource(api_key, allow_simulation=False)
        self._gdp_source = WorldBankProvider("JP")
        self._cache: Optional[CountryMacroContext] = None

    @property
    def currency(self) -> str:
        return "JPY"

    @property
    def source(self) -> str:
        return "FRED (Japan)"

    async def get_historical(
        self,
        start_date: str,
        end_date: str,
    ) -> pd.DataFrame:
        """
        Obtiene el histórico de policy rate para Japón.
        """
        try:
            result = await self._source.fetch_series(
                "IRLTLT01JPM156N",
                start_date=start_date,
                end_date=end_date,
                limit=1000
            )

            if not result or not result.get("observations"):
                logger.warning(
                    "No historical Japan observations for %s -> %s",
                    start_date,
                    end_date,
                )
                return pd.DataFrame(columns=["date", "policy_rate"])

            rows = []
            for obs in result["observations"]:
                date_str = obs.get("date")
                value_str = obs.get("value")

                if not date_str or value_str is None:
                    continue

                try:
                    rows.append({
                        "date": pd.to_datetime(date_str),
                        "policy_rate": float(value_str),
                    })
                except (ValueError, TypeError):
                    continue

            if not rows:
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
            logger.error("Error fetching historical Japan data: %s", e)
            return pd.DataFrame(columns=["date", "policy_rate"])

    async def get_context(self, force_refresh: bool = False) -> CountryMacroContext:
        if not force_refresh and self._cache:
            return self._cache

        try:
            # Obtener policy rate de FRED
            rate_data = await self._source.fetch_series("IRLTLT01JPM156N", limit=2)
            policy_rate = None

            if rate_data and rate_data.get("observations"):
                obs = rate_data["observations"]
                if obs and obs[0].get("value"):
                    policy_rate = float(obs[0]["value"])

            # Obtener GDP Growth de World Bank
            gdp_context = await self._gdp_source.get_context(force_refresh=force_refresh)
            gdp_growth = gdp_context.gdp_growth if gdp_context.available else None

            available = policy_rate is not None

            context = CountryMacroContext(
                currency="JPY",
                policy_rate=policy_rate,
                gdp_growth=gdp_growth,
                inflation=gdp_context.inflation if gdp_context.available else None,
                unemployment=None,
                timestamp=datetime.now(),
                source="FRED (Japan) + World Bank",
                available=available,
                is_fallback=not available,
                reason="Long-term rates como policy_rate para Japan" if available else "FRED Japan no disponible",
            )

            self._cache = context
            return context

        except Exception as e:
            logger.error(f"Error fetching Japan data: {e}")
            return CountryMacroContext(
                currency="JPY",
                available=False,
                is_fallback=True,
                reason=f"FRED Japan error: {str(e)}",
                timestamp=datetime.now(),
                source="FRED",
            )
