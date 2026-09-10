"""
Macro Differential Provider.

Calcula diferenciales macro entre la moneda base y la moneda quote.

Principios:
- No inventa datos para monedas sin fuente disponible.
- No confunde ausencia de datos con neutralidad económica.
- Los diferenciales entregados al DecisionPipeline están normalizados
  al dominio [-1, +1].
- base_rate / quote_rate conservan sus unidades económicas originales (%).
"""

import pandas as pd
from dataclasses import dataclass
from typing import Optional

from .differential_status import MacroDataStatus
from .registry import CountryMacroRegistry


@dataclass
class MacroDifferentialResult:
    """Resultado del cálculo de diferenciales macro."""

    base_currency: str
    quote_currency: str

    policy_differential: Optional[float]
    growth_differential: Optional[float]
    inflation_differential: Optional[float]

    base_rate: Optional[float]
    quote_rate: Optional[float]

    status: MacroDataStatus
    base_available: bool
    quote_available: bool
    reason: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "base": self.base_currency,
            "quote": self.quote_currency,
            "policy_differential": self.policy_differential,
            "growth_differential": self.growth_differential,
            "inflation_differential": self.inflation_differential,
            "base_rate": self.base_rate,
            "quote_rate": self.quote_rate,
            "status": self.status.value,
            "base_available": self.base_available,
            "quote_available": self.quote_available,
            "reason": self.reason,
        }


class MacroDifferentialProvider:
    """
    Calcula diferenciales macro base-vs-quote.

    La implementación inicial solamente dispone de datos macro de USD
    a través de FRED. Por diseño, una moneda sin proveedor no recibe
    valores sintéticos.
    """

    # FRED actualmente cubre USD.
    # Escalas explícitas para convertir diferencias económicas a [-1, +1].
    #
    # Estas constantes representan la sensibilidad del score, no límites
    # económicos absolutos.
    POLICY_SCALE = 4.0
    GROWTH_SCALE = 4.0
    INFLATION_SCALE = 4.0

    def __init__(self):
        pass

    @classmethod
    def is_supported(cls, currency: str) -> bool:
        return CountryMacroRegistry.is_supported(currency)

    @staticmethod
    def _normalize(value: float, scale: float) -> float:
        """
        Normaliza una diferencia firmada a [-1, +1].

        No se permite que el diferencial bruto escape del dominio del
        contrato canónico.
        """
        if scale <= 0:
            raise ValueError("normalization scale must be positive")

        normalized = value / scale
        return max(-1.0, min(1.0, normalized))

    @classmethod
    def calculate(
        cls,
        base_currency: str,
        quote_currency: str,
        base_macro: Optional[dict],
        quote_macro: Optional[dict],
    ) -> MacroDifferentialResult:
        """
        Calcula los diferenciales entre dos contextos macro.

        ``base_macro`` y ``quote_macro`` deben contener, cuando estén
        disponibles, un ``summary`` con:
          - fed_funds
          - gdp_growth

        La tasa monetaria se utiliza como proxy común para el diferencial
        de tasas en esta primera implementación.
        """

        base = base_currency.upper()
        quote = quote_currency.upper()

        base_available = base_macro is not None and cls.is_supported(base)
        quote_available = quote_macro is not None and cls.is_supported(quote)

        # Determinar disponibilidad de cada componente
        base_summary = base_macro.get("summary", {}) if base_available else {}
        quote_summary = quote_macro.get("summary", {}) if quote_available else {}

        base_rate = base_summary.get("policy_rate")
        if base_rate is None:
            base_rate = base_summary.get("fed_funds")

        quote_rate = quote_summary.get("policy_rate")
        if quote_rate is None:
            quote_rate = quote_summary.get("fed_funds")
        base_growth = base_summary.get("gdp_growth")
        quote_growth = quote_summary.get("gdp_growth")

        # FULL requiere todos los componentes disponibles
        policy_available = base_rate is not None and quote_rate is not None
        growth_available = base_growth is not None and quote_growth is not None
        rate_available = base_rate is not None and quote_rate is not None  # mismo que policy por ahora

        if policy_available and growth_available:
            status = MacroDataStatus.FULL
        elif policy_available and growth_available:
            status = MacroDataStatus.PARTIAL
        elif base_available or quote_available:
            status = MacroDataStatus.PARTIAL
        else:
            status = MacroDataStatus.UNAVAILABLE

        if not (base_available and quote_available):
            return MacroDifferentialResult(
                base_currency=base,
                quote_currency=quote,
                policy_differential=None,
                growth_differential=None,
                inflation_differential=None,
                base_rate=base_rate,
                quote_rate=quote_rate,
                status=status,
                base_available=base_available,
                quote_available=quote_available,
                reason=(
                    "Macro differential unavailable because both base and "
                    "quote country macro datasets are required."
                ),
            )

        base_rate = base_summary.get("policy_rate")
        if base_rate is None:
            base_rate = base_summary.get("fed_funds")

        quote_rate = quote_summary.get("policy_rate")
        if quote_rate is None:
            quote_rate = quote_summary.get("fed_funds")

        base_growth = base_summary.get("gdp_growth")
        quote_growth = quote_summary.get("gdp_growth")

        if base_rate is None or quote_rate is None:
            policy_diff = None
        else:
            rate_diff = base_rate - quote_rate
            policy_diff = cls._normalize(rate_diff, cls.POLICY_SCALE)

        if base_growth is None or quote_growth is None:
            growth_diff = None
        else:
            growth_diff = cls._normalize(
                base_growth - quote_growth,
                cls.GROWTH_SCALE,
            )

        # Inflation differential
        base_inflation = base_summary.get("inflation")
        quote_inflation = quote_summary.get("inflation")
        if base_inflation is None or quote_inflation is None:
            inflation_diff = None
        else:
            inflation_diff = cls._normalize(
                base_inflation - quote_inflation,
                cls.INFLATION_SCALE,
            )

        return MacroDifferentialResult(
            base_currency=base,
            quote_currency=quote,
            policy_differential=policy_diff,
            growth_differential=growth_diff,
            inflation_differential=inflation_diff,
            base_rate=base_rate,
            quote_rate=quote_rate,
            status=status,
            base_available=base_available,
            quote_available=quote_available,
            reason=None,
        )

    
    @classmethod
    def calculate_historical(
        cls,
        base_currency: str,
        quote_currency: str,
        base_series: pd.DataFrame,
        quote_series: pd.DataFrame,
        price_dates: pd.DatetimeIndex,
    ) -> pd.Series:
        """
        Calcula policy differential histórico Point-in-Time.

        Para cada fecha t:
            base_policy(t)  = última observación base <= t
            quote_policy(t) = última observación quote <= t

        No utiliza valores futuros.
        """

        if len(price_dates) == 0:
            return pd.Series(dtype="float64", name="policy_diff")

        def normalize_series(
            series: pd.DataFrame,
            column_name: str,
        ) -> pd.DataFrame:
            required = {"date", "policy_rate"}
            missing = required - set(series.columns)

            if missing:
                raise ValueError(
                    f"Serie histórica {column_name} incompleta. "
                    f"Faltan columnas: {sorted(missing)}"
                )

            result = series[["date", "policy_rate"]].copy()

            result["date"] = pd.to_datetime(
                result["date"],
                errors="coerce",
            ).dt.normalize()

            result["policy_rate"] = pd.to_numeric(
                result["policy_rate"],
                errors="coerce",
            )

            result = (
                result
                .dropna(subset=["date", "policy_rate"])
                .drop_duplicates(subset=["date"], keep="last")
                .sort_values("date")
                .reset_index(drop=True)
            )

            return result.rename(
                columns={"policy_rate": column_name}
            )

        # Normalizar las fechas de precios.
        prices = pd.DataFrame({
            "date": pd.to_datetime(
                pd.DatetimeIndex(price_dates),
                errors="coerce",
            ).normalize()
        })

        prices = (
            prices
            .dropna(subset=["date"])
            .drop_duplicates(subset=["date"])
            .sort_values("date")
            .reset_index(drop=True)
        )

        base = normalize_series(base_series, "base_policy")
        quote = normalize_series(quote_series, "quote_policy")

        # Asegurar exactamente el mismo dtype temporal.
        common_dtype = prices["date"].dtype

        base["date"] = base["date"].astype(common_dtype)
        quote["date"] = quote["date"].astype(common_dtype)

        # Point-in-Time: última observación disponible <= fecha de precio.
        macro = pd.merge_asof(
            prices,
            base,
            on="date",
            direction="backward",
        )

        macro = pd.merge_asof(
            macro.sort_values("date"),
            quote,
            on="date",
            direction="backward",
        )

        # Eliminar fechas donde todavía no existe una observación
        # macro disponible. Nunca rellenar artificialmente.
        macro = macro.dropna(
            subset=["base_policy", "quote_policy"]
        )

        # Diferencial canónico:
        # base policy rate - quote policy rate.
        macro["policy_diff_raw"] = (
            macro["base_policy"] - macro["quote_policy"]
        )

        # Misma normalización que calculate().
        macro["policy_diff"] = (
            macro["policy_diff_raw"] / cls.POLICY_SCALE
        ).clip(-1.0, 1.0)

        return (
            macro
            .set_index("date")["policy_diff"]
            .rename("policy_diff")
        )

