"""Módulo de datos macro."""

from .providers.fred import FREDProvider
from .providers.chain import ChainCNYProvider
from .providers.world_bank import WorldBankProvider
from .providers.bolivia import BoliviaProvider
from .providers.switzerland import SwitzerlandProvider
from .providers.euro import EuroProvider
from .registry import CountryMacroRegistry

# Limpiar registry antes de registrar
CountryMacroRegistry.clear()

# 1. Países con policy rate
CountryMacroRegistry.register(FREDProvider())           # USD
CountryMacroRegistry.register(EuroProvider())           # EUR
CountryMacroRegistry.register(SwitzerlandProvider())    # CHF

# 2. Datos estructurales (GDP, Inflation, Unemployment)
#    World Bank para el resto de países
for code in ["GB", "JP", "MX", "BR", "AR"]:
    CountryMacroRegistry.register(WorldBankProvider(code))

# 3. Bolivia - Provider específico (sin policy_rate)
CountryMacroRegistry.register(BoliviaProvider())

# 4. China - Chain (World Bank + Investing fallback)
CountryMacroRegistry.register(ChainCNYProvider())

print(f"✅ Monedas soportadas: {sorted(CountryMacroRegistry.get_supported_currencies())}")
