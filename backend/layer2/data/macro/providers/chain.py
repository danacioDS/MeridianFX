"""
Chain Provider - Combina múltiples proveedores en una cadena de fallback.

CNBS/NBS → primary
World Bank → secondary
Investing.com → fallback (temporal)
"""

import logging
from datetime import datetime
from typing import Optional

from .base import CountryMacroContext, CountryMacroProvider
from .cnbs import CNBSProvider
from .world_bank import WorldBankProvider
from .investing_com import InvestingComProvider

logger = logging.getLogger(__name__)


class ChainCNYProvider(CountryMacroProvider):
    """
    Proveedor en cadena para CNY.
    
    Primero intenta CNBS/NBS, luego World Bank, luego Investing.com.
    """

    def __init__(self):
        self._cnbs = CNBSProvider()
        self._worldbank = WorldBankProvider()
        self._investing = InvestingComProvider()
        self._cache: Optional[CountryMacroContext] = None

    @property
    def currency(self) -> str:
        return "CNY"

    @property
    def source(self) -> str:
        return "CNBS/NBS → World Bank → Investing.com (chain)"

    async def get_context(self, force_refresh: bool = False) -> CountryMacroContext:
        """Obtiene contexto macro de CNY con cadena de fallback."""
        if not force_refresh and self._cache:
            return self._cache

        # 1. Intentar CNBS/NBS primero
        cnbs_context = await self._cnbs.get_context(force_refresh=force_refresh)
        if cnbs_context.available:
            logger.info("CNY: usando datos de CNBS/NBS")
            self._cache = cnbs_context
            return cnbs_context

        # 2. Si CNBS no tiene datos, usar World Bank
        logger.info("CNY: CNBS no disponible, usando World Bank")
        wb_context = await self._worldbank.get_context(force_refresh=force_refresh)
        if wb_context.available:
            logger.info("CNY: usando datos de World Bank")
            self._cache = wb_context
            return wb_context

        # 3. Si World Bank no tiene datos, usar Investing.com (temporal)
        logger.info("CNY: World Bank no disponible, usando Investing.com fallback")
        investing_context = await self._investing.get_context(force_refresh=force_refresh)
        if investing_context.available:
            logger.info("CNY: usando datos de Investing.com")
            self._cache = investing_context
            return investing_context

        # 4. Si todos fallan, devolver fallback explícito
        logger.warning("CNY: ningún proveedor disponible, usando fallback explícito")
        context = CountryMacroContext(
            currency="CNY",
            available=False,
            is_fallback=True,
            reason="CNBS/NBS, World Bank e Investing.com no tienen datos disponibles",
            timestamp=datetime.now(),
            source="Chain (no data)",
        )
        self._cache = context
        return context
