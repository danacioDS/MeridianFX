"""
Country Macro Registry - Registro de proveedores de datos macro por país.
"""

from typing import Dict, Optional, Set

from .providers.base import CountryMacroProvider


class CountryMacroRegistry:
    """
    Registro de proveedores macro por moneda.
    
    Esta es la fuente de verdad para saber qué monedas tienen datos macro disponibles.
    """
    _providers: Dict[str, CountryMacroProvider] = {}

    @classmethod
    def register(cls, provider: CountryMacroProvider) -> None:
        """Registra un proveedor."""
        cls._providers[provider.currency.upper()] = provider

    @classmethod
    def get(cls, currency: str) -> Optional[CountryMacroProvider]:
        """Obtiene un proveedor por moneda."""
        return cls._providers.get(currency.upper())

    @classmethod
    def get_supported_currencies(cls) -> Set[str]:
        """Obtiene el conjunto de monedas soportadas."""
        return set(cls._providers.keys())

    @classmethod
    def is_supported(cls, currency: str) -> bool:
        """Verifica si una moneda tiene proveedor."""
        return currency.upper() in cls._providers

    @classmethod
    def clear(cls) -> None:
        """Limpia el registro (para tests)."""
        cls._providers.clear()
