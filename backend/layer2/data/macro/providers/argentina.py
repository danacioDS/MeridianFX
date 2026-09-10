"""
Argentina Provider - Datos macro de Argentina via FRED + World Bank.

Series FRED:
- IRSTCB01ARA156N: Long-term interest rates (proxy para policy_rate)
- World Bank para GDP Growth
"""

import logging
import pandas as pd
from datetime import datetime
from typing import Optional

from backend.layer2.data.sources.fred import FredDataSource
from .world_bank import WorldBankProvider
from .base import CountryMacroContext, CountryMacroProvider

logger = logging.getLogger(__name__)


class ArgentinaProvider(CountryMacroProvider):
    def __init__(self, api_key: Optional[str] = None):
        self._source = FredDataSource(api_key, allow_simulation=False)
        self._gdp_source = WorldBankProvider("AR")
        self._cache: Optional[CountryMacroContext] = None

    @property
    def currency(self) -> str:
        return "ARS"

    @property
    def source(self) -> str:
        return "FRED (Argentina) + World Bank"

    async def get_historical(self, start_date: str, end_date: str) -> pd.DataFrame:
        try:
            result = await self._source.fetch_series("IRSTCB01ARA156N", start_date=start_date, end_date=end_date, limit=1000)
            if not result or not result.get("observations"):
                return pd.DataFrame(columns=["date", "policy_rate"])
            rows = []
            for obs in result["observations"]:
                date_str = obs.get("date")
                value_str = obs.get("value")
                if not date_str or value_str is None:
                    continue
                try:
                    rows.append({"date": pd.to_datetime(date_str), "policy_rate": float(value_str)})
                except (ValueError, TypeError):
                    continue
            if not rows:
                return pd.DataFrame(columns=["date", "policy_rate"])
            df = pd.DataFrame(rows)
            return df[["date", "policy_rate"]].dropna().drop_duplicates(subset=["date"]).sort_values("date").reset_index(drop=True)
        except Exception as e:
            logger.error("Error fetching historical Argentina data: %s", e)
            return pd.DataFrame(columns=["date", "policy_rate"])

    async def get_context(self, force_refresh: bool = False) -> CountryMacroContext:
        if not force_refresh and self._cache:
            return self._cache
        try:
            rate_data = await self._source.fetch_series("IRSTCB01ARA156N", limit=2)
            policy_rate = None
            if rate_data and rate_data.get("observations"):
                obs = rate_data["observations"]
                if obs and obs[0].get("value"):
                    policy_rate = float(obs[0]["value"])
            gdp_context = await self._gdp_source.get_context(force_refresh=force_refresh)
            gdp_growth = gdp_context.gdp_growth if gdp_context.available else None
            available = policy_rate is not None
            context = CountryMacroContext(
                currency="ARS",
                policy_rate=policy_rate,
                gdp_growth=gdp_growth,
                inflation=None,
                unemployment=None,
                timestamp=datetime.now(),
                source="FRED (Argentina) + World Bank",
                available=available,
                is_fallback=not available,
                reason="Long-term rates como policy_rate para Argentina" if available else "FRED Argentina no disponible",
            )
            self._cache = context
            return context
        except Exception as e:
            logger.error(f"Error fetching Argentina data: {e}")
            return CountryMacroContext(currency="ARS", available=False, is_fallback=True, reason=f"FRED Argentina error: {str(e)}", timestamp=datetime.now(), source="FRED")
