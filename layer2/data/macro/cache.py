"""
Macro Cache — Almacenamiento en disco de datos macro.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class MacroCache:
    """
    Caché en disco para datos macro.
    
    Evita llamadas innecesarias a FRED y permite
    que el sistema funcione con datos antiguos si
    la API no está disponible.
    """
    
    CACHE_DIR = "cache/macro"
    DEFAULT_TTL_HOURS = 24  # 1 día
    
    def __init__(self, ttl_hours: int = DEFAULT_TTL_HOURS):
        self.ttl_hours = ttl_hours
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Asegura que el directorio de caché existe."""
        os.makedirs(self.CACHE_DIR, exist_ok=True)
    
    def _get_cache_path(self, key: str) -> str:
        """Obtiene la ruta del archivo de caché."""
        return os.path.join(self.CACHE_DIR, f"{key}.json")
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un valor de la caché.
        
        Args:
            key: Clave de caché
            
        Returns:
            Datos cacheados o None si no existen o están expirados
        """
        cache_path = self._get_cache_path(key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
            
            # Verificar TTL
            cached_at = datetime.fromisoformat(data.get("cached_at", "2000-01-01T00:00:00"))
            if datetime.now() - cached_at > timedelta(hours=self.ttl_hours):
                logger.debug(f"Cache expired for {key}")
                return None
            
            logger.debug(f"Cache hit for {key}")
            return data.get("value")
            
        except Exception as e:
            logger.warning(f"Error reading cache for {key}: {e}")
            return None
    
    def set(self, key: str, value: Dict[str, Any]) -> None:
        """
        Guarda un valor en la caché.
        
        Args:
            key: Clave de caché
            value: Datos a guardar
        """
        cache_path = self._get_cache_path(key)
        
        try:
            data = {
                "cached_at": datetime.now().isoformat(),
                "value": value
            }
            
            with open(cache_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.debug(f"Cached {key}")
            
        except Exception as e:
            logger.warning(f"Error writing cache for {key}: {e}")
    
    def clear(self, key: Optional[str] = None) -> None:
        """
        Limpia la caché.
        
        Args:
            key: Clave específica o None para limpiar todo
        """
        if key:
            cache_path = self._get_cache_path(key)
            if os.path.exists(cache_path):
                os.remove(cache_path)
        else:
            for file in os.listdir(self.CACHE_DIR):
                os.remove(os.path.join(self.CACHE_DIR, file))
    
    def get_age(self, key: str) -> Optional[int]:
        """
        Obtiene la edad de un elemento en caché en segundos.
        
        Args:
            key: Clave de caché
            
        Returns:
            Edad en segundos o None si no existe
        """
        cache_path = self._get_cache_path(key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
            
            cached_at = datetime.fromisoformat(data.get("cached_at", "2000-01-01T00:00:00"))
            return int((datetime.now() - cached_at).total_seconds())
            
        except Exception:
            return None
