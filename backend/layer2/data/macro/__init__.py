"""Módulo de datos macro."""

from .providers.fred import FREDProvider
from .providers.chain import ChainCNYProvider
from .providers.world_bank import WorldBankProvider
from .providers.bolivia import BoliviaProvider
from .providers.switzerland import SwitzerlandProvider
from .providers.euro import EuroProvider
from .providers.uk import UKProvider
from .providers.japan import JapanProvider
from .providers.mexico import MexicoProvider
from .providers.brazil import BrazilProvider
from .providers.argentina import ArgentinaProvider
from .registry import CountryMacroRegistry

# Limpiar registry antes de registrar
CountryMacroRegistry.clear()

# 1. Países con policy rate (implementan get_historical)
CountryMacroRegistry.register(FREDProvider())           # USD
CountryMacroRegistry.register(EuroProvider())           # EUR
CountryMacroRegistry.register(SwitzerlandProvider())    # CHF
CountryMacroRegistry.register(UKProvider())             # GBP - con get_historical()
CountryMacroRegistry.register(JapanProvider())          # JPY - con get_historical()
CountryMacroRegistry.register(MexicoProvider())         # MXN - con get_historical()
CountryMacroRegistry.register(BrazilProvider())          # BRL - con get_historical()
CountryMacroRegistry.register(ArgentinaProvider())        # ARS - con get_historical()

# 3. Bolivia - Provider específico (sin policy_rate)
CountryMacroRegistry.register(BoliviaProvider())

# 4. China - Chain (World Bank + Investing fallback)
CountryMacroRegistry.register(ChainCNYProvider())

print(f"✅ Monedas soportadas: {sorted(CountryMacroRegistry.get_supported_currencies())}")
