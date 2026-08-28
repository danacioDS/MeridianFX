"""
Macro Service — Servicio unificado para datos macro.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .cache import MacroCache
from ..sources.fred import FredDataSource
from .transformer import MacroTransformer

logger = logging.getLogger(__name__)


class MacroService:
    """
    Servicio de datos macro unificado.
    
    Orquesta:
    1. FRED API
    2. Caché
    3. Transformación
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.source = FredDataSource(api_key)
        self.cache = MacroCache()
        self.transformer = MacroTransformer()
    
    async def get_macro_context(
        self,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Obtiene el contexto macro completo.
        
        Args:
            force_refresh: Si es True, ignora la caché
            
        Returns:
            Contexto macro estructurado
        """
        cache_key = "macro_context"
        
        # Intentar obtener de caché
        if not force_refresh:
            cached = self.cache.get(cache_key)
            if cached:
                logger.debug("Macro context from cache")
                return cached
        
        # Obtener datos de FRED
        logger.info("Fetching macro data from FRED...")
        raw_data = await self.source.get_macro_context()
        
        # Transformar
        macro_context = self.transformer.transform(raw_data)
        
        # Guardar en caché
        self.cache.set(cache_key, macro_context)
        
        return macro_context
    
    async def get_series(self, series_id: str) -> Optional[Dict]:
        """
        Obtiene una serie específica.
        
        Args:
            series_id: ID de la serie FRED
            
        Returns:
            Datos de la serie
        """
        cache_key = f"series_{series_id}"
        
        # Intentar de caché
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        # Obtener de FRED
        data = await self.source.fetch_series(series_id)
        if data:
            self.cache.set(cache_key, data)
            return data
        
        return None
    
    def get_cache_status(self) -> Dict[str, Any]:
        """Obtiene el estado de la caché."""
        macro_context_age = self.cache.get_age("macro_context")
        
        return {
            "macro_context_cached": macro_context_age is not None,
            "macro_context_age_seconds": macro_context_age,
            "cache_dir": self.cache.CACHE_DIR,
            "ttl_hours": self.cache.ttl_hours,
        }
    
    def clear_cache(self) -> None:
        """Limpia la caché."""
        self.cache.clear()
        logger.info("Macro cache cleared")
