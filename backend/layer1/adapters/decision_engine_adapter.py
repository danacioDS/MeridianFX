"""
DecisionEngineAdapter - Convierte DecisionEngine legacy en PredictionArtifact canónico.
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from backend.layer2.engine import DecisionEngine
from backend.layer2.data.macro.service import MacroService
from backend.layer2.data.macro.transformer import MacroTransformer
from backend.layer2.data.macro.canonical_adapter import CanonicalMacroAdapter

from backend.src.meridian_fx.decision.contracts.prediction import (
    PredictionArtifact,
    ConfidenceInterval,
    MacroRegime,
    ShapValue,
    Reproducibility
)

logger = logging.getLogger(__name__)


class DecisionEngineAdapter:
    """
    Adaptador que convierte la salida del DecisionEngine legacy
    en un PredictionArtifact canónico para el DecisionPipeline.
    """
    
    def __init__(self, engine: Optional[DecisionEngine] = None):
        self._engine = engine or DecisionEngine()
        self._macro_service = MacroService()
        self.git_commit = "unknown"
        self.docker_image = "meridianfx:latest"
        self.mlflow_run_id = "unknown"
    
    def _get_macro_regime(self) -> MacroRegime:
        """Obtiene el régimen macro desde MacroService."""
        try:
            import asyncio
            macro_context = asyncio.run(self._macro_service.get_macro_context())
            macro_regime_dict = MacroTransformer().to_regime(macro_context)
            canonical_values = CanonicalMacroAdapter.to_canonical(macro_regime_dict)
            return MacroRegime(
                risk=canonical_values["risk"],
                policy=canonical_values["policy"],
                growth=canonical_values["growth"],
                inflation=canonical_values["inflation"],
            )
        except Exception as e:
            logger.warning(f"Failed to get macro regime: {e}")
            return MacroRegime(
                risk="UNKNOWN",
                policy="UNKNOWN",
                growth="UNKNOWN",
                inflation="UNKNOWN",
            )
    
    def get_prediction_artifact(
        self,
        pair: str,
        horizon_days: int = 30,
        macro_regime: Optional[MacroRegime] = None,
    ) -> Optional[PredictionArtifact]:
        """
        Obtiene un PredictionArtifact canónico para un par.
        """
        # 1. Obtener forecast del engine legacy
        forecast = self._engine.get_forecast(pair)
        if not forecast:
            return None
        
        # 2. Obtener régimen macro (real o proporcionado)
        if macro_regime is None:
            macro_regime = self._get_macro_regime()
        
        # 3. Extraer datos
        probability = forecast.get('probability', 0.5)
        direction = forecast.get('direction', 'NEUTRAL')
        expected_return = forecast.get('expected_return', 0.0)
        expected_volatility = forecast.get('expected_volatility', 0.12)
        model_version = forecast.get('model', {}).get('version', 'xgb-v1.0')
        model_type = forecast.get('model', {}).get('type', 'xgboost')
        timestamp = datetime.now(timezone.utc)
        
        # 4. Determinar probability_up
        if direction == "UP":
            probability_up = probability
        elif direction == "DOWN":
            probability_up = 1 - probability
        else:
            probability_up = 0.5
        
        # 5. Construir confidence_interval
        lower = max(0.0, probability_up - expected_volatility * 0.5)
        upper = min(1.0, probability_up + expected_volatility * 0.5)
        confidence_interval = ConfidenceInterval(lower=lower, upper=upper)
        
        # 6. Construir shap_values
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
        
        # 7. Construir artifact con macro_regime real
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
