"""
DecisionEngineAdapter - Convierte DecisionEngine legacy en PredictionArtifact canónico.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from backend.layer2.engine import DecisionEngine

# Importar desde la ubicación correcta
from backend.src.meridian_fx.decision.contracts.prediction import (
    PredictionArtifact,
    ConfidenceInterval,
    MacroRegime,
    ShapValue,
    Reproducibility
)


class DecisionEngineAdapter:
    """
    Adaptador que convierte la salida del DecisionEngine legacy
    en un PredictionArtifact canónico para el DecisionPipeline.
    """
    
    def __init__(self, engine: Optional[DecisionEngine] = None):
        self._engine = engine or DecisionEngine()
        self.git_commit = "unknown"
        self.docker_image = "meridianfx:latest"
        self.mlflow_run_id = "unknown"
    
    def get_prediction_artifact(
        self,
        pair: str,
        horizon_days: int = 30
    ) -> Optional[PredictionArtifact]:
        """
        Obtiene un PredictionArtifact canónico para un par.
        """
        # 1. Obtener forecast del engine legacy
        forecast = self._engine.get_forecast(pair)
        if not forecast:
            return None
        
        # 2. Extraer datos
        probability = forecast.get('probability', 0.5)
        direction = forecast.get('direction', 'NEUTRAL')
        expected_return = forecast.get('expected_return', 0.0)
        expected_volatility = forecast.get('expected_volatility', 0.12)
        model_version = forecast.get('model', {}).get('version', 'xgb-v1.0')
        model_type = forecast.get('model', {}).get('type', 'xgboost')
        timestamp = datetime.now(timezone.utc)
        
        # 3. Determinar probability_up
        if direction == "UP":
            probability_up = probability
        elif direction == "DOWN":
            probability_up = 1 - probability
        else:
            probability_up = 0.5
        
        # 4. Construir confidence_interval
        lower = max(0.0, probability_up - expected_volatility * 0.5)
        upper = min(1.0, probability_up + expected_volatility * 0.5)
        confidence_interval = ConfidenceInterval(lower=lower, upper=upper)
        
        # 5. Construir shap_values
        shap_values = []
        shap_data = forecast.get('shap')
        if shap_data:
            contributions = shap_data.get('contributions', [])
            for c in contributions[:20]:
                feature = c.get('feature', 'unknown')
                contribution = c.get('contribution', 0)
                if feature and contribution != 0:
                    shap_values.append(
                        ShapValue(feature=feature, value=contribution)
                    )
        
        # 6. Macro regime (desde forecast o por defecto)
        macro_regime = MacroRegime(
            risk="UNKNOWN",
            policy="UNKNOWN",
            growth="UNKNOWN",
            inflation="UNKNOWN"
        )
        
        # 7. Construir artifact
        return PredictionArtifact(
            prediction_id=str(uuid.uuid4()),
            model_id=f"{model_type}_{pair.replace('/', '_')}",
            model_version=model_version,
            pair=pair,
            prediction_timestamp=timestamp,
            horizon_days=horizon_days,
            probability_up=probability_up,
            expected_return=expected_return,
            expected_volatility=expected_volatility,
            confidence_interval=confidence_interval,
            regime_id=f"regime_{timestamp.strftime('%Y%m%d')}",
            macro_regime=macro_regime,
            rag_signal_ids=[],
            shap_values=shap_values,
            feature_snapshot_id=f"snapshot_{timestamp.strftime('%Y%m%d%H%M%S')}",
            dataset_id=f"dataset_{timestamp.strftime('%Y%m%d')}",
            feature_version="1.0",
            as_of=timestamp,
            research_gate_status="APPROVED",
            reproducibility=Reproducibility(
                git_commit=self.git_commit,
                docker_image=self.docker_image,
                mlflow_run_id=self.mlflow_run_id
            ),
            created_at=timestamp
        )
    
    def get_drivers(self, pair: str) -> Dict[str, Any]:
        """Wrapper legacy para drivers."""
        model = self._engine._get_model_for_pair(pair, 'xgboost')
        if not model:
            return {"error": f"No model found for {pair}"}
        
        return {
            "shap_values": [],
            "feature_importance": {},
            "macro_regime": {},
            "sentiment": {}
        }
