"""
Model Registry — Research Layer v5.0 §11.1

Tracks all models that have passed the Research Gate.
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class ModelArtifact:
    """ModelArtifact — Research → Production (§11.1)"""
    model_id: str
    model_version: str
    model_type: str  # "ARIMA" | "ElasticNet" | "XGBoost" | "Ensemble"
    model_file: str
    
    training: Dict[str, Any]
    research_gate: Dict[str, Any]
    performance: Dict[str, Any]
    reproducibility: Dict[str, Any]
    
    lifecycle: str  # "CANDIDATE" | "DEPLOYED" | "MONITORED" | "RETIRED"
    created_at: str
    updated_at: str


@dataclass
class PredictionArtifact:
    """PredictionArtifact — Research → Layer 2 (§11.2)"""
    prediction_id: str
    model_id: str
    model_version: str
    pair: str
    prediction_timestamp: str
    horizon_days: int
    
    probability_up: float
    expected_return: float
    expected_volatility: float
    confidence_interval: Dict[str, float]
    
    regime_id: Optional[str]
    macro_regime: Dict[str, str]
    rag_signal_ids: List[str]
    shap_values: List[Dict[str, Any]]
    
    feature_snapshot_id: str
    dataset_id: str
    feature_version: str
    as_of: str
    
    research_gate_status: str  # "APPROVED" | "REJECTED" | "PENDING"
    reproducibility: Dict[str, str]
    created_at: str


class ModelRegistry:
    """Registry for tracking model artifacts."""
    
    def __init__(self, registry_path: str = "models/registry.json"):
        self.registry_path = registry_path
        self.models: Dict[str, ModelArtifact] = {}
        self._load()
    
    def _load(self):
        if os.path.exists(self.registry_path):
            with open(self.registry_path, 'r') as f:
                data = json.load(f)
                for item in data:
                    artifact = ModelArtifact(**item)
                    self.models[artifact.model_id] = artifact
    
    def _save(self):
        data = [asdict(m) for m in self.models.values()]
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
        with open(self.registry_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def register(self, artifact: ModelArtifact) -> None:
        self.models[artifact.model_id] = artifact
        self._save()
    
    def get(self, model_id: str) -> Optional[ModelArtifact]:
        return self.models.get(model_id)
    
    def get_active(self, model_type: str) -> Optional[ModelArtifact]:
        for m in self.models.values():
            if m.model_type == model_type and m.lifecycle == "DEPLOYED":
                return m
        return None
    
    def list_all(self) -> List[ModelArtifact]:
        return list(self.models.values())
