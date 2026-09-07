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

from dataclasses import dataclass
from typing import Optional

from .differential_status import MacroDataStatus


@dataclass
class MacroDifferentialResult:
    """Resultado del cálculo de diferenciales macro."""

    base_currency: str
    quote_currency: str

    policy_differential: Optional[float]
    growth_differential: Optional[float]
    normalized_rate_differential: Optional[float]

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
            "normalized_rate_differential": self.normalized_rate_differential,
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
    SUPPORTED_CURRENCIES = {"USD"}

    # Escalas explícitas para convertir diferencias económicas a [-1, +1].
    #
    # Estas constantes representan la sensibilidad del score, no límites
    # económicos absolutos.
    POLICY_SCALE = 4.0
    GROWTH_SCALE = 4.0
    RATE_SCALE = 4.0

    def __init__(self):
        pass

    @classmethod
    def is_supported(cls, currency: str) -> bool:
        return currency.upper() in cls.SUPPORTED_CURRENCIES

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

        if base_available and quote_available:
            status = MacroDataStatus.FULL
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
                normalized_rate_differential=None,
                base_rate=None,
                quote_rate=None,
                status=status,
                base_available=base_available,
                quote_available=quote_available,
                reason=(
                    "Macro differential unavailable because both base and "
                    "quote country macro datasets are required."
                ),
            )

        base_summary = base_macro.get("summary", {})
        quote_summary = quote_macro.get("summary", {})

        base_rate = base_summary.get("fed_funds")
        quote_rate = quote_summary.get("fed_funds")

        base_growth = base_summary.get("gdp_growth")
        quote_growth = quote_summary.get("gdp_growth")

        if base_rate is None or quote_rate is None:
            rate_diff = None
            normalized_rate_diff = None
            policy_diff = None
        else:
            rate_diff = base_rate - quote_rate
            policy_diff = cls._normalize(rate_diff, cls.POLICY_SCALE)
            normalized_rate_diff = cls._normalize(rate_diff, cls.RATE_SCALE)

        if base_growth is None or quote_growth is None:
            growth_diff = None
        else:
            growth_diff = cls._normalize(
                base_growth - quote_growth,
                cls.GROWTH_SCALE,
            )

        return MacroDifferentialResult(
            base_currency=base,
            quote_currency=quote,
            policy_differential=policy_diff,
            growth_differential=growth_diff,
            normalized_rate_differential=normalized_rate_diff,
            base_rate=base_rate,
            quote_rate=quote_rate,
            status=status,
            base_available=base_available,
            quote_available=quote_available,
            reason=None,
        )
