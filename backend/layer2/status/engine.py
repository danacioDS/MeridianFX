"""
Status Engine — Monitorea el estado real del sistema.
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class StatusEngine:
    """
    Obtiene el estado real de todos los componentes del sistema.
    """
    
    def __init__(self):
        self.registry_path = "models/registry.json"
        self._registry = None
    
    def load_registry(self) -> Dict[str, Any]:
        """Carga el registro de modelos."""
        if self._registry is not None:
            return self._registry
        
        if not os.path.exists(self.registry_path):
            return {"models": []}
        
        try:
            with open(self.registry_path, 'r') as f:
                self._registry = json.load(f)
            return self._registry
        except Exception as e:
            logger.error(f"Error loading registry: {e}")
            return {"models": []}
    
    def get_models_status(self) -> List[Dict[str, Any]]:
        """
        Obtiene el estado de todos los modelos.
        """
        registry = self.load_registry()
        models = registry.get("models", [])
        
        status_list = []
        for model in models:
            pair = model.get("pair", "unknown")
            is_active = model.get("active", False)
            created_at = model.get("created_at")
            metrics = model.get("metrics", {})
            
            # Calcular edad del modelo
            age_days = None
            if created_at:
                try:
                    created_date = datetime.fromisoformat(created_at)
                    age_days = (datetime.now() - created_date).days
                except:
                    pass
            
            # Determinar estado
            if is_active:
                model_status = "active"
            elif age_days and age_days > 30:
                model_status = "stale"
            else:
                model_status = "inactive"
            
            status_list.append({
                "pair": pair,
                "status": model_status,
                "active": is_active,
                "last_trained": created_at,
                "age_days": age_days,
                "version": model.get("version", "unknown"),
                "accuracy": metrics.get("accuracy", 0.0),
                "auc": metrics.get("auc", 0.0),
                "model_type": model.get("model_type", "unknown")
            })
        
        return status_list
    
    def get_models_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen del estado de los modelos.
        """
        models = self.get_models_status()
        
        active = sum(1 for m in models if m.get("active"))
        stale = sum(1 for m in models if m.get("status") == "stale")
        inactive = sum(1 for m in models if not m.get("active"))
        
        return {
            "total": len(models),
            "active": active,
            "stale": stale,
            "inactive": inactive,
            "models": models
        }
    
    def get_data_sources_status(self) -> List[Dict[str, Any]]:
        """
        Obtiene el estado de las fuentes de datos.
        """
        sources = []
        
        # Yahoo Finance
        yahoo_status = self._check_yahoo()
        sources.append({
            "name": "yahoo_finance",
            "status": yahoo_status["status"],
            "latency_ms": yahoo_status.get("latency_ms"),
            "last_success": yahoo_status.get("last_success")
        })
        
        # FRED
        fred_status = self._check_fred()
        sources.append({
            "name": "fred",
            "status": fred_status["status"],
            "latency_ms": fred_status.get("latency_ms"),
            "last_success": fred_status.get("last_success")
        })
        
        # Alpha Vantage
        alpha_status = self._check_alpha_vantage()
        sources.append({
            "name": "alpha_vantage",
            "status": alpha_status["status"],
            "latency_ms": alpha_status.get("latency_ms"),
            "last_success": alpha_status.get("last_success")
        })
        
        # Twelve Data
        twelve_status = self._check_twelve_data()
        sources.append({
            "name": "twelve_data",
            "status": twelve_status["status"],
            "latency_ms": twelve_status.get("latency_ms"),
            "last_success": twelve_status.get("last_success")
        })
        
        return sources
    
    def _check_yahoo(self) -> Dict[str, Any]:
        """Verifica el estado de Yahoo Finance."""
        try:
            import requests
            start = time.time()
            response = requests.get(
                "https://query1.finance.yahoo.com/v8/finance/chart/USDJPY=X",
                timeout=5
            )
            latency = (time.time() - start) * 1000
            
            if response.status_code == 200:
                return {"status": "online", "latency_ms": round(latency, 2), "last_success": datetime.now().isoformat()}
            else:
                return {"status": "degraded", "latency_ms": round(latency, 2)}
        except Exception as e:
            logger.warning(f"Yahoo check failed: {e}")
            return {"status": "offline"}
    
    def _check_fred(self) -> Dict[str, Any]:
        """Verifica el estado de FRED."""
        api_key = os.getenv("FRED_API_KEY")
        if not api_key:
            return {"status": "offline", "reason": "FRED_API_KEY not set"}
        
        try:
            import requests
            start = time.time()
            response = requests.get(
                f"https://api.stlouisfed.org/fred/series/observations",
                params={"series_id": "DFF", "api_key": api_key, "limit": 1},
                timeout=5
            )
            latency = (time.time() - start) * 1000
            
            if response.status_code == 200:
                return {"status": "online", "latency_ms": round(latency, 2), "last_success": datetime.now().isoformat()}
            else:
                return {"status": "degraded", "latency_ms": round(latency, 2)}
        except Exception as e:
            logger.warning(f"FRED check failed: {e}")
            return {"status": "offline"}
    
    def _check_alpha_vantage(self) -> Dict[str, Any]:
        """Verifica el estado de Alpha Vantage."""
        api_key = os.getenv("ALPHA_VANTAGE_KEY")
        if not api_key:
            return {"status": "offline", "reason": "ALPHA_VANTAGE_KEY not set"}
        
        try:
            import requests
            start = time.time()
            response = requests.get(
                "https://www.alphavantage.co/query",
                params={"function": "CURRENCY_EXCHANGE_RATE", "from_currency": "USD", "to_currency": "JPY", "apikey": api_key},
                timeout=5
            )
            latency = (time.time() - start) * 1000
            
            if response.status_code == 200 and "Realtime Currency Exchange Rate" in response.json():
                return {"status": "online", "latency_ms": round(latency, 2), "last_success": datetime.now().isoformat()}
            else:
                return {"status": "degraded", "latency_ms": round(latency, 2)}
        except Exception as e:
            logger.warning(f"Alpha Vantage check failed: {e}")
            return {"status": "offline"}
    
    def _check_twelve_data(self) -> Dict[str, Any]:
        """Verifica el estado de Twelve Data."""
        api_key = os.getenv("TWELVE_DATA_KEY")
        if not api_key:
            return {"status": "offline", "reason": "TWELVE_DATA_KEY not set"}
        
        try:
            import requests
            start = time.time()
            response = requests.get(
                "https://api.twelvedata.com/price",
                params={"symbol": "USD/JPY", "apikey": api_key},
                timeout=5
            )
            latency = (time.time() - start) * 1000
            
            if response.status_code == 200 and "price" in response.json():
                return {"status": "online", "latency_ms": round(latency, 2), "last_success": datetime.now().isoformat()}
            else:
                return {"status": "degraded", "latency_ms": round(latency, 2)}
        except Exception as e:
            logger.warning(f"Twelve Data check failed: {e}")
            return {"status": "offline"}
    
    def get_llm_status(self) -> List[Dict[str, Any]]:
        """
        Obtiene el estado de los proveedores LLM.
        """
        providers = []
        
        # Groq
        groq_key = os.getenv("GROQ_API_KEY")
        providers.append({
            "provider": "groq",
            "status": "online" if groq_key else "offline",
            "model": "llama-3.1-70b-versatile" if groq_key else None,
            "reason": "GROQ_API_KEY not set" if not groq_key else None
        })
        
        # GLM
        glm_key = os.getenv("GLM_API_KEY")
        providers.append({
            "provider": "glm",
            "status": "online" if glm_key else "offline",
            "model": "glm-4-flash" if glm_key else None,
            "reason": "GLM_API_KEY not set" if not glm_key else None
        })
        
        # Gemini
        gemini_key = os.getenv("GEMINI_API_KEY")
        providers.append({
            "provider": "gemini",
            "status": "online" if gemini_key else "offline",
            "model": "gemini-1.5-flash" if gemini_key else None,
            "reason": "GEMINI_API_KEY not set" if not gemini_key else None
        })
        
        return providers
    
    def get_cache_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado de la caché.
        """
        cache_status = {
            "status": "online",
            "memory_used_mb": 0,
            "keys": 0,
            "hit_rate": 0.0
        }
        
        # Verificar caché de macro
        macro_cache_path = "cache/macro"
        if os.path.exists(macro_cache_path):
            files = os.listdir(macro_cache_path)
            cache_status["keys"] = len(files)
            cache_status["memory_used_mb"] = self._get_dir_size(macro_cache_path) / (1024 * 1024)
        
        # Verificar caché de forecast
        forecast_cache_path = "cache/forecast_cache.json"
        if os.path.exists(forecast_cache_path):
            cache_status["keys"] += 1
        
        return cache_status
    
    def _get_dir_size(self, path: str) -> int:
        """Calcula el tamaño de un directorio."""
        total = 0
        for root, dirs, files in os.walk(path):
            for f in files:
                fp = os.path.join(root, f)
                if os.path.exists(fp):
                    total += os.path.getsize(fp)
        return total
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Obtiene el estado general del sistema.
        """
        models = self.get_models_status()
        
        # Determinar estado general
        system_status = "HEALTHY"
        reasons = []
        
        # Verificar modelos
        active_count = sum(1 for m in models if m.get("active"))
        if active_count == 0:
            system_status = "DEGRADED"
            reasons.append("No active models")
        elif active_count < len(models) / 2:
            system_status = "DEGRADED"
            reasons.append("Less than half models active")
        
        # Verificar fuentes de datos
        sources = self.get_data_sources_status()
        online_sources = sum(1 for s in sources if s.get("status") == "online")
        if online_sources == 0:
            system_status = "DEGRADED"
            reasons.append("No data sources online")
        elif online_sources < len(sources) / 2:
            system_status = "DEGRADED"
            reasons.append("Less than half data sources online")
        
        return {
            "status": system_status,
            "reason": "All systems operational" if not reasons else "; ".join(reasons),
            "uptime_seconds": 0,  # TODO: implementar uptime
            "memory_usage_mb": self._get_memory_usage()
        }
    
    def _get_memory_usage(self) -> float:
        """Obtiene el uso de memoria en MB."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)
        except:
            return 0.0
    
    def get_full_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado completo del sistema.
        """
        return {
            "system": self.get_system_health(),
            "models": self.get_models_status(),
            "models_summary": self.get_models_summary(),
            "data_sources": self.get_data_sources_status(),
            "llm_providers": self.get_llm_status(),
            "cache": self.get_cache_status()
        }
