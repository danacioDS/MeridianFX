"""
Data Provider con fallback entre múltiples fuentes.
Yahoo Finance → Alpha Vantage → Twelve Data

Contrato canónico:
- DataFrame con índice datetime
- índice timezone-naive
- orden cronológico ascendente
- columnas: Open, High, Low, Close, Volume
- iloc[-1] siempre representa el dato más reciente
"""

import pandas as pd
from datetime import datetime, timezone

from .sources.twelve import TwelveDataSource
from .sources.alpha_vantage import AlphaVantageSource
from .sources.yahoo import YahooSource


class DataProvider:
    def __init__(self):
        self.sources = [
            ("yahoo", YahooSource.fetch),
            ("alpha", AlphaVantageSource.fetch),
            ("twelve", TwelveDataSource.fetch),
        ]

        self.last_provider = None
        self.last_success = None
        self.fallback_used = False

    @staticmethod
    def _normalize(df: pd.DataFrame) -> pd.DataFrame:
        """Apply the canonical DataProvider contract."""

        if df is None or df.empty:
            raise ValueError("Empty dataframe")

        df = df.copy()

        # Canonical datetime index
        df.index = pd.to_datetime(df.index)

        # Remove timezone if present
        if getattr(df.index, "tz", None) is not None:
            df.index = df.index.tz_localize(None)

        # Canonical column names
        required = ["Open", "High", "Low", "Close", "Volume"]

        for column in required:
            if column not in df.columns:
                if column == "Volume":
                    df[column] = 0.0
                elif "Close" in df.columns:
                    df[column] = df["Close"]
                else:
                    raise ValueError(
                        f"Missing required column: {column}"
                    )

        # Numeric contract
        for column in required:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

        # Close is mandatory
        df = df.dropna(subset=["Close"])

        # Chronological ascending order
        df = df.sort_index()

        # Remove duplicated timestamps
        df = df[~df.index.duplicated(keep="last")]

        if df.empty:
            raise ValueError("No valid rows after normalization")

        return df

    def get_historical(
        self,
        pair: str,
        period: str = "1y",
        interval: str = "1d",
    ) -> dict:

        # Canonical period aliases.
        # Yahoo Finance uses "6mo", not "6m".
        period_aliases = {
            "6m": "6mo",
        }
        period = period_aliases.get(period, period)

        for source_name, source_func in self.sources:
            try:
                print(f"📥 Intentando {source_name}...")

                raw_df = source_func(
                    pair,
                    period,
                    interval,
                )

                df = self._normalize(raw_df)

                if len(df) < 20:
                    raise ValueError(
                        f"Insufficient data: {len(df)} rows"
                    )

                self.last_provider = source_name
                self.last_success = datetime.now(timezone.utc)
                self.fallback_used = (
                    source_name != self.sources[0][0]
                )

                last_date = df.index[-1]

                # Compare using date only to avoid timezone issues
                today = datetime.now(timezone.utc).date()
                last_day = last_date.date()

                days_ago = (today - last_day).days

                if days_ago <= 1:
                    freshness = "FRESH"
                elif days_ago <= 5:
                    freshness = "STALE"
                else:
                    freshness = "OLD"

                last_price = float(
                    df["Close"].iloc[-1]
                )

                print(
                    f"✅ {source_name} funcionó "
                    f"({len(df)} filas)"
                )

                return {
                    "data": df,
                    "provider": source_name,
                    "fallback_used": self.fallback_used,
                    "timestamp": datetime.now(timezone.utc),
                    "freshness": freshness,
                    "last_price": last_price,
                    "last_date": last_date,
                }

            except Exception as exc:
                print(
                    f"⚠️ {source_name} falló: "
                    f"{type(exc).__name__}: {str(exc)[:100]}"
                )
                continue

        raise Exception(
            f"Todas las fuentes de datos fallaron para {pair}"
        )

    def get_latest_price(self, pair: str) -> float:
        result = self.get_historical(
            pair,
            period="5d",
            interval="1d",
        )

        return result["last_price"]

    def get_status(self) -> dict:
        return {
            "last_provider": self.last_provider,
            "last_success": (
                self.last_success.isoformat()
                if self.last_success
                else None
            ),
            "fallback_used": self.fallback_used,
            "sources_available": [
                source[0]
                for source in self.sources
            ],
            "status": (
                "HEALTHY"
                if self.last_success
                else "UNKNOWN"
            ),
        }
