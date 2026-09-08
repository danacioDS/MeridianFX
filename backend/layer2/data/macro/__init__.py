"""Módulo de datos macro."""

from .providers.fred import FREDProvider
from .providers.chain import ChainCNYProvider
from .providers.world_bank import WorldBankProvider
from .providers.trading_economics import TradingEconomicsProvider
from .registry import CountryMacroRegistry

# Limpiar registry antes de registrar
CountryMacroRegistry.clear()

# Registrar proveedores disponibles

# 1. USD - FRED (datos reales)
CountryMacroRegistry.register(FREDProvider())

# 2. CNY - Chain (CNBS → World Bank → Investing)
CountryMacroRegistry.register(ChainCNYProvider())

# 3. EUR - World Bank (Euro Area)
CountryMacroRegistry.register(WorldBankProvider("EMU"))

# 4. GBP - World Bank (United Kingdom)
CountryMacroRegistry.register(WorldBankProvider("GB"))

# 5. JPY - World Bank (Japan)
CountryMacroRegistry.register(WorldBankProvider("JP"))

# 6. CHF - World Bank (Switzerland)
CountryMacroRegistry.register(WorldBankProvider("CH"))

# 7. MXN - World Bank (Mexico)
CountryMacroRegistry.register(WorldBankProvider("MX"))

# 8. BRL - World Bank (Brazil)
CountryMacroRegistry.register(WorldBankProvider("BR"))

# 9. ARS - World Bank (Argentina)
CountryMacroRegistry.register(WorldBankProvider("AR"))

# 10. BOB - World Bank (Bolivia)
CountryMacroRegistry.register(WorldBankProvider("BO"))

print(f"✅ Monedas soportadas: {sorted(CountryMacroRegistry.get_supported_currencies())}")
