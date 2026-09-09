"""
Switzerland Provider - Datos macro de Suiza.

Fuentes:
- GDP: World Bank
- Inflation: World Bank
- Unemployment: World Bank
- Policy Rate: FRED IRLTLT01CHM156N (long-term rates)
"""

import logging
import pandas as pd
from datetime import datetime
from typing import Optional

from .world_bank import WorldBankProvider
from backend.layer2.data.sources.fred import FredDataSource
from .base import CountryMacroContext, CountryMacroProvider

logger = logging.getLogger(__name__)


class SwitzerlandProvider(CountryMacroProvider):
    """Proveedor de datos macro de Suiza."""

    def __init__(self, api_key: Optional[str] = None):
        self._source = WorldBankProvider("CH")
        self._fred_source = FredDataSource(api_key, allow_simulation=False)
        self._cache: Optional[CountryMacroContext] = None

    @property
    def currency(self) -> str:
        return "CHF"

    @property
    def source(self) -> str:
        return "World Bank + FRED"

    async def get_historical(
        self,
        start_date: str,
        end_date: str,
    ) -> pd.DataFrame:
        """Obtiene el histórico de policy rate para Suiza (FRED proxy)."""
        try:
            result = await self._fred_source.fetch_series(
                "IRLTLT01CHM156N",
                start_date=start_date,
                end_date=end_date,
                limit=1000
            )

            if not result or not result.get("observations"):
                logger.warning(
                    "No historical Switzerland observations for %s -> %s",
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
            logger.error("Error fetching historical Switzerland data: %s", e)
            return pd.DataFrame(columns=["date", "policy_rate"])

    async def get_context(self, force_refresh: bool = False) -> CountryMacroContext:
        if not force_refresh and self._cache:
            return self._cache

        try:
            # Obtener datos de World Bank
            ctx = await self._source.get_context(force_refresh=force_refresh)
            
            # Obtener policy rate de FRED
            rate_data = await self._fred_source.fetch_series("IRLTLT01CHM156N", limit=2)
            policy_rate = None

            if rate_data and rate_data.get("observations"):
                obs = rate_data["observations"]
                if obs and obs[0].get("value"):
                    policy_rate = float(obs[0]["value"])

            available = policy_rate is not None

            context = CountryMacroContext(
                currency="CHF",
                policy_rate=policy_rate,
                gdp_growth=ctx.gdp_growth,
                inflation=ctx.inflation,
                unemployment=ctx.unemployment,
                timestamp=datetime.now(),
                source=self.source,
                available=ctx.available and available,
                is_fallback=not available,
                reason="FRED long-term rates como policy_rate para Suiza" if available else "FRED Switzerland no disponible",
            )

            self._cache = context
            return context

        except Exception as e:
            logger.error(f"Error fetching Switzerland data: {e}")
            return CountryMacroContext(
                currency="CHF",
                available=False,
                is_fallback=True,
                reason=f"Error fetching data: {str(e)}",
                timestamp=datetime.now(),
                source="World Bank",
            )
