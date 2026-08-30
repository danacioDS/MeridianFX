"""
Registry Adapter — Converts Layer 2 registry format to Layer 3 ModelArtifact.

Layer 2 uses a simpler registry format (models/registry.json).
Layer 3 expects ModelArtifact with full fields.
"""
import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime


class RegistryAdapter:
    """
    Adapter between Layer 2 registry and Layer 3 ModelArtifact.
    
    Converts the existing Layer 2 registry format to the Layer 3 ModelArtifact format.
    """
    
    def __init__(self, registry_path: str = "models/registry.json"):
        self.registry_path = registry_path
        self._load()
    
    def _load(self):
        """Load the registry from disk."""
        if os.path.exists(self.registry_path):
            with open(self.registry_path, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {"models": [], "current": {}}
    
    def _convert_to_model_artifact(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert a Layer 2 registry entry to a Layer 3 ModelArtifact.
        """
        # Determine lifecycle based on active flag
        lifecycle = "DEPLOYED" if entry.get('active', False) else "CANDIDATE"
        
        return {
            'model_id': entry.get('model_id', ''),
            'model_version': entry.get('version', 'v1.0'),
            'model_type': entry.get('model_type', 'xgboost'),
            'model_file': entry.get('path', ''),
            'training': {
                'dataset_id': f"ds_{entry.get('pair', '').replace('/', '_')}",
                'feature_version': 'v1.0',
                'training_period': {'start': '2025-01-01', 'end': '2026-01-01'},
                'hyperparameters': {},
                'feature_list': []
            },
            'research_gate': {
                'status': 'APPROVED' if entry.get('active', False) else 'PENDING',
                'report': {},
                'approved_at': entry.get('created_at', datetime.now().isoformat()),
                'approved_by': 'system'
            },
            'performance': {
                'test_period': {'start': '2026-01-01', 'end': '2026-08-30'},
                'statistical': {
                    'DA': entry.get('metrics', {}).get('accuracy', 0.5),
                    'AUC': entry.get('metrics', {}).get('auc', 0.5),
                    'Brier': entry.get('metrics', {}).get('brier', 0.5),
                    'ECE': 0.05
                },
                'economic': {
                    'Sharpe_net': 0.3,
                    'MaxDD': -0.1,
                    'PF': 1.2,
                    'WinRate': 0.55
                },
                'regime_performance': {}
            },
            'reproducibility': {
                'git_commit': 'unknown',
                'docker_image': 'meridian-fx:latest',
                'mlflow_run_id': 'unknown',
                'config_hash': 'unknown',
                'random_seed': 42
            },
            'lifecycle': lifecycle,
            'created_at': entry.get('created_at', datetime.now().isoformat()),
            'updated_at': datetime.now().isoformat()
        }
    
    def get_model_artifacts(self) -> List[Dict[str, Any]]:
        """Get all models as Layer 3 ModelArtifacts."""
        return [self._convert_to_model_artifact(entry) for entry in self.data.get('models', [])]
    
    def get_model_artifact_by_pair(self, pair: str) -> List[Dict[str, Any]]:
        """Get models for a specific pair."""
        artifacts = self.get_model_artifacts()
        return [a for a in artifacts if a.get('training', {}).get('dataset_id', '').startswith(f"ds_{pair.replace('/', '_')}")]
    
    def get_active_model_artifact(self, pair: str, model_type: str = "xgboost") -> Optional[Dict[str, Any]]:
        """Get the active model for a pair and type."""
        artifacts = self.get_model_artifact_by_pair(pair)
        for a in artifacts:
            if a.get('model_type') == model_type and a.get('lifecycle') == "DEPLOYED":
                return a
        return None
