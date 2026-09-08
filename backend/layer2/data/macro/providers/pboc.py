"""
PBoC Provider - Datos macro de China.

Proveedor preparado para integración con fuentes oficiales del
People's Bank of China (PBoC) / National Bureau of Statistics (NBS).

IMPORTANTE:
- No contiene valores económicos hardcodeados.
- No genera datos simulados.
- Si la fuente oficial no está integrada o falla, devuelve
  available=False y valores None.
"""

from datetime import datetime
from typing import Optional

from .base import CountryMacroContext, CountryMacroProvider


class PBOCProvider(CountryMacroProvider):
    """Proveedor de datos macro de China mediante fuentes oficiales."""

    def __init__(self):
        self._cache: Optional[CountryMacroContext] = None

    @property
    def currency(self) -> str:
        return "CNY"

    @property
    def source(self) -> str:
        return "PBoC / NBS"

    async def get_context(
        self,
        force_refresh: bool = False,
    ) -> CountryMacroContext:
        """Obtiene datos macro oficiales de China."""

        if not force_refresh and self._cache:
            return self._cache

        context = CountryMacroContext(
            currency="CNY",
            policy_rate=None,
            gdp_growth=None,
            inflation=None,
            unemployment=None,
            yield_10y=None,
            yield_2y=None,
            timestamp=datetime.now(),
            source=self.source,
            available=False,
            is_fallback=False,
            reason=(
                "Integración con fuentes oficiales PBoC/NBS "
                "pendiente."
            ),
        )

        self._cache = context
        return context
