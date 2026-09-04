"""
Adaptador para DecisionEngine migrado
Convierte la nueva API (per-pair) a la interfaz esperada por los routers
"""

from typing import Optional, Dict, Any
from layer2.engine import DecisionEngine

class DecisionEngineAdapter:
    """Adaptador para mantener compatibilidad durante la migración"""
    
    def __init__(self, engine: DecisionEngine):
        self._engine = engine
    
    def get_model_for_pair(self, pair: str, model_type: str = 'xgboost'):
        """Wrapper para _get_model_for_pair"""
        return self._engine._get_model_for_pair(pair, model_type)
    
    def get_drivers(self, pair: str) -> Dict[str, Any]:
        """Reimplementación de get_drivers usando la nueva API"""
        model = self._engine._get_model_for_pair(pair, 'xgboost')
        if not model:
            return {"error": f"No model found for {pair}"}
        
        # Obtener features y SHAP values
        # ... implementar usando model
        return {
            "shap_values": [],
            "feature_importance": {},
            "macro_regime": {},
            "sentiment": {}
        }
