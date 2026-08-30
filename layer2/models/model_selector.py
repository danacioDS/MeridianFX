"""
Model Selector — Layer 2 consumes approved models from Layer 3.

Layer 3 owns model research, validation, and registration.
Layer 2 owns model selection and prediction.
"""
from typing import Dict, Any, Optional, List
from .registry_adapter import RegistryAdapter


class ModelSelector:
    """
    Selects the best approved model for a given pair.
    
    Uses the RegistryAdapter to convert Layer 2 registry format
    to Layer 3 ModelArtifact format.
    """
    
    def __init__(self, registry_path: str = "models/registry.json"):
        self.adapter = RegistryAdapter(registry_path)
    
    def get_best_model(self, pair: str, model_type: str = "xgboost") -> Optional[Dict[str, Any]]:
        """
        Get the best approved model for a pair.
        
        Priority:
        1. DEPLOYED models (highest)
        2. MONITORED models
        3. CANDIDATE models
        """
        artifacts = self.adapter.get_model_artifact_by_pair(pair)
        pair_models = [a for a in artifacts if a.get('model_type') == model_type]
        
        if not pair_models:
            return None
        
        # Sort by lifecycle: DEPLOYED > MONITORED > CANDIDATE
        lifecycle_priority = {"DEPLOYED": 0, "MONITORED": 1, "CANDIDATE": 2}
        
        pair_models.sort(
            key=lambda m: (lifecycle_priority.get(m.get('lifecycle', 'CANDIDATE'), 99), 
                          -m.get('performance', {}).get('economic', {}).get('Sharpe_net', 0))
        )
        
        return pair_models[0] if pair_models else None
    
    def get_active_model_path(self, pair: str, model_type: str = "xgboost") -> Optional[str]:
        """Get the file path of the best model."""
        model = self.get_best_model(pair, model_type)
        if model:
            return model.get('model_file')
        return None
    
    def list_available_models(self, pair: str) -> List[Dict[str, Any]]:
        """List all available models for a pair."""
        artifacts = self.adapter.get_model_artifact_by_pair(pair)
        
        return [
            {
                'model_id': a.get('model_id', ''),
                'model_type': a.get('model_type', ''),
                'version': a.get('model_version', ''),
                'lifecycle': a.get('lifecycle', ''),
                'sharpe_net': a.get('performance', {}).get('economic', {}).get('Sharpe_net', 0),
                'da': a.get('performance', {}).get('statistical', {}).get('DA', 0),
            }
            for a in artifacts
        ]
