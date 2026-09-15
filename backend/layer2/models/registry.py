"""
Model Registry - Gestión de versiones de modelos.

Promotion policy (v2.5.1+):
    A model is promoted to DEPLOYED only if it passes the promotion gate.
    The gate is defined by MIN_AUC and MIN_N_SAMPLES below.
    Models below the gate remain CANDIDATE and are not served to users.

    See scripts/audit_registry.py for the audit tool.
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

# Promotion gate — a model must satisfy BOTH conditions to be DEPLOYED.
MIN_AUC = 0.52
MIN_N_SAMPLES = 300


def _passes_gate(metrics: Dict) -> bool:
    """Check whether a model's metrics satisfy the promotion gate."""
    auc = metrics.get("auc", 0.0)
    n = metrics.get("n_samples", 0)
    try:
        auc = float(auc)
        n = int(n)
    except (ValueError, TypeError):
        return False
    return auc >= MIN_AUC and n >= MIN_N_SAMPLES

class ModelRegistry:
    def __init__(self, registry_path: str = "models/registry.json"):
        self.registry_path = registry_path
        self.registry = self._load()
    
    def _load(self) -> Dict:
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                # Corrupted or unreadable registry — fall back to empty.
                return {'models': [], 'current': {}}
        return {'models': [], 'current': {}}
    
    def _save(self):
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
        with open(self.registry_path, 'w') as f:
            json.dump(self.registry, f, indent=2, default=str)
    
    def register(self, pair: str, model_type: str, version: str, 
                 metrics: Dict, path: str) -> str:
        """Registra un nuevo modelo."""
        model_id = f"{pair}_{model_type}_{version}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Extraer solo valores serializables
        clean_metrics = {}
        for k, v in metrics.items():
            if isinstance(v, (int, float, str, bool, list, dict)):
                clean_metrics[k] = v
            elif hasattr(v, 'tolist'):
                clean_metrics[k] = v.tolist()
            else:
                clean_metrics[k] = str(v)
        
        entry = {
            'model_id': model_id,
            'pair': pair,
            'model_type': model_type,
            'version': version,
            'path': path,
            'metrics': clean_metrics,
            'created_at': datetime.now().isoformat(),
            'active': False
        }
        
        self.registry['models'].append(entry)

        # Promotion policy (v2.5.1+):
        # A model is only activated if it passes the gate AND is better
        # than the current active model. Otherwise it stays CANDIDATE.
        passes_gate = _passes_gate(clean_metrics)

        if passes_gate:
            current = self.get_active(pair, model_type)
            if current is None or clean_metrics.get('auc', 0) > current.get('metrics', {}).get('auc', 0):
                self.activate(pair, model_type, model_id)

        self._save()
        return model_id
    
    def activate(self, pair: str, model_type: str, model_id: str, force: bool = False):
        """Activa un modelo específico.

        By default, refuses to activate a model that does not pass the gate.
        Use force=True to override (e.g. for migration scripts).
        """
        target = None
        for entry in self.registry['models']:
            if entry['model_id'] == model_id:
                target = entry
                break

        if target is None:
            raise ValueError(f"Model {model_id} not found")

        if not force and not _passes_gate(target.get('metrics', {})):
            raise ValueError(
                f"Model {model_id} does not pass the promotion gate "
                f"(auc >= {MIN_AUC}, n_samples >= {MIN_N_SAMPLES})"
            )

        for entry in self.registry['models']:
            if entry['pair'] == pair and entry['model_type'] == model_type:
                entry['active'] = False

        target['active'] = True
        self.registry['current'][f"{pair}_{model_type}"] = model_id
        self._save()
    
    def get_active(self, pair: str, model_type: str) -> Optional[Dict]:
        """Obtiene el modelo activo."""
        model_id = self.registry['current'].get(f"{pair}_{model_type}")
        if not model_id:
            return None
        
        for entry in self.registry['models']:
            if entry['model_id'] == model_id:
                return entry
        return None
    
    def list_models(self, pair: Optional[str] = None) -> List[Dict]:
        """Lista todos los modelos, opcionalmente filtrados por par."""
        models = self.registry['models']
        if pair:
            models = [m for m in models if m['pair'] == pair]
        return sorted(models, key=lambda x: x['created_at'], reverse=True)
    
    def compare(self, pair: str, model_type: str) -> Dict:
        """Compara todas las versiones de un modelo."""
        models = [m for m in self.registry['models'] 
                  if m['pair'] == pair and m['model_type'] == model_type]
        
        if not models:
            return {'error': 'No models found'}
        
        return {
            'pair': pair,
            'model_type': model_type,
            'versions': [
                {
                    'version': m['version'],
                    'model_id': m['model_id'],
                    'metrics': m['metrics'],
                    'created_at': m['created_at'],
                    'active': m['active']
                }
                for m in models
            ]
        }
