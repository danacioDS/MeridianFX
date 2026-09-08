"""Módulo de datos macro."""

from .providers.fred import FREDProvider
from .providers.chain import ChainCNYProvider
from .providers.ecb import ECBProvider
from .providers.trading_economics import TradingEconomicsProvider
from .registry import CountryMacroRegistry

# Limpiar registry antes de registrar
CountryMacroRegistry.clear()

# Providers primarios / especializados
CountryMacroRegistry.register(FREDProvider())       # USD
CountryMacroRegistry.register(ChainCNYProvider())   # CNY: FRED -> Investing
CountryMacroRegistry.register(ECBProvider())        # EUR

# Trading Economics para las monedas restantes
for currency in [
    "ARS",
    "MXN",
    "BRL",
    "CHF",
    "GBP",
    "JPY",
    "BOB",
]:
    CountryMacroRegistry.register(
        TradingEconomicsProvider(currency)
    )
