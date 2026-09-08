"""
Chain Provider - Combina múltiples proveedores en una cadena de fallback.

FRED China → primary
Investing.com → fallback
"""

import logging
from datetime import datetime
from typing import Optional

from .base import CountryMacroContext, CountryMacroProvider
from .fred_china import FREDChinaProvider
from .investing_com import InvestingComProvider

logger = logging.getLogger(__name__)


class ChainCNYProvider(CountryMacroProvider):
    """
    Proveedor en cadena para CNY.
    
    Primero intenta FRED China, si falla usa Investing.com.
    """

    def __init__(self):
        self._fred = FREDChinaProvider()
        self._investing = InvestingComProvider()
        self._cache: Optional[CountryMacroContext] = None

    @property
    def currency(self) -> str:
        return "CNY"

    @property
    def source(self) -> str:
        return "FRED + Investing.com (chain)"

    async def get_context(self, force_refresh: bool = False) -> CountryMacroContext:
        """Obtiene contexto macro de CNY con cadena de fallback."""
        if not force_refresh and self._cache:
            return self._cache

        # 1. Intentar FRED primero
        fred_context = await self._fred.get_context(force_refresh=force_refresh)
        
        if fred_context.available:
            logger.info("CNY: usando datos de FRED")
            self._cache = fred_context
            return fred_context

        # 2. Si FRED no tiene datos, usar Investing.com
        logger.info("CNY: FRED no tiene datos, usando Investing.com fallback")
        investing_context = await self._investing.get_context(force_refresh=force_refresh)
        
        if investing_context.available:
            logger.info("CNY: usando datos de Investing.com")
            self._cache = investing_context
            return investing_context

        # 3. Si ambos fallan, devolver fallback explícito
        logger.warning("CNY: ningún proveedor disponible, usando fallback explícito")
        context = CountryMacroContext(
            currency="CNY",
            available=False,
            is_fallback=True,
            reason="FRED y Investing.com no tienen datos disponibles",
            timestamp=datetime.now(),
            source="Chain (no data)",
        )
        self._cache = context
        return context
