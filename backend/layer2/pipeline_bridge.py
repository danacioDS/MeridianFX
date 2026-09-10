"""
Bridge entre Layer 2 (datos) y DecisionPipeline (decisión)
Reutiliza DecisionEngineAdapter para construir PredictionArtifact.
"""

from typing import Dict, Any
from datetime import datetime, timezone

from backend.src.meridian_fx.decision.pipeline import DecisionPipeline, PipelineInputs
from backend.src.meridian_fx.decision.contracts import PredictionArtifact

from backend.layer2.config import (
    BASE_SIZE,
    HISTORICAL_RELIABILITY,
    MAX_EXPOSURE,
    REQUIRED_MINIMUM_EDGE_BPS,
)
from backend.layer2.data.provider import DataProvider
from backend.layer2.features.technical import TechnicalFeatures
from backend.layer2.engine import DecisionEngine
from backend.layer1.adapters.decision_engine_adapter import DecisionEngineAdapter
from backend.layer1.utils.pair_normalizer import normalize_pair

# Nuevos imports para el régimen macro
from backend.layer2.data.macro.service import MacroService
from backend.layer2.data.macro.transformer import MacroTransformer
from backend.layer2.data.macro.canonical_adapter import CanonicalMacroAdapter
from backend.src.meridian_fx.decision.contracts.prediction import MacroRegime

# Import para trazabilidad
from backend.layer2.data.macro.differential_status import MacroDifferentialStatus, MacroDataStatus

# Import para el proveedor de diferenciales
from backend.layer2.data.macro.differential_provider import MacroDifferentialProvider


class PipelineBridge:
    """Conecta Layer 2 con el DecisionPipeline usando el adapter existente."""
    
    def __init__(self, pipeline: DecisionPipeline):
        self.pipeline = pipeline
        self.data_provider = DataProvider()
        self.engine = DecisionEngine()
        self.adapter = DecisionEngineAdapter(self.engine)
        self.macro_service = MacroService()
        self.macro_transformer = MacroTransformer()
        self.differential_provider = MacroDifferentialProvider()
    
    async def evaluate_pair(self, pair: str, horizon_days: int = 30) -> Dict[str, Any]:
        """
        Evalúa un par usando el pipeline canónico.
        Versión async que obtiene el régimen macro correctamente.
        """
        # 1. Obtener contexto macro (async)
        macro_context = await self.macro_service.get_macro_context()
        macro_regime_dict = self.macro_transformer.to_regime(macro_context)
        canonical_values = CanonicalMacroAdapter.to_canonical(macro_regime_dict)
        
        macro_regime = MacroRegime(
            risk=canonical_values["risk"],
            policy=canonical_values["policy"],
            growth=canonical_values["growth"],
            inflation=canonical_values["inflation"],
        )
        
        # 2. Obtener PredictionArtifact con régimen real
        artifact = self.adapter.get_prediction_artifact(
            pair=pair,
            horizon_days=horizon_days,
            macro_regime=macro_regime,
        )
        if artifact is None:
            return {
                "error": "Failed to create PredictionArtifact",
                "pair": pair,
                "horizon_days": horizon_days
            }
        
        # 3. Obtener datos reales
        data = self.data_provider.get_historical(pair, period='1y')
        if not data or 'data' not in data:
            return {"error": "No data available", "pair": pair}
        
        # 4. Generar features
        features = TechnicalFeatures.generate(data['data'])
        
        # 5. Calcular diferenciales macro
        base, quote = pair.split('/')
        
        # Obtener contextos por país usando el Registry
        base_context = await self.macro_service.get_country_context(base)
        quote_context = await self.macro_service.get_country_context(quote)
        
        # Convertir a dict para MacroDifferentialProvider
        base_macro = base_context.to_dict() if base_context.available else None
        quote_macro = quote_context.to_dict() if quote_context.available else None
        
        differential_result = self.differential_provider.calculate(
            base_currency=base,
            quote_currency=quote,
            base_macro=base_macro,
            quote_macro=quote_macro,
        )
        
        # 6. Construir PipelineInputs con diferenciales reales (o None)
        inputs = self._build_inputs(
            artifact=artifact,
            differential_result=differential_result,
        )
        
        # 7. Ejecutar pipeline
        result = self.pipeline.build(inputs)
        
        # 8. Retornar resultado completo con metadatos de trazabilidad
        return {
            "pair": pair,
            "horizon_days": horizon_days,
            "decision": result.decision.model_dump(),
            "gate": result.gate.model_dump() if result.gate else None,
            "vix": result.vix,
            "regime": result.regime,
            "sizing": result.sizing,
            "fusion": result.fusion,
            "costs": result.costs,
            "economic": result.economic,
            "quality": result.quality,
            "signals": result.signals,
            "artifact": artifact.model_dump(),
            "macro_data_status": differential_result.to_dict(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _build_inputs(
        self,
        artifact: PredictionArtifact,
        differential_result,
    ) -> PipelineInputs:
        """
        Construye PipelineInputs usando el timestamp del artifact
        y los diferenciales calculados.
        """
        as_of = artifact.as_of
        
        # Obtener valores del resultado de diferenciales
        # Si son None, se usa 0.0 como fallback (PipelineInputs requiere float)
        policy_diff = differential_result.policy_differential if differential_result.policy_differential is not None else 0.0
        growth_diff = differential_result.growth_differential if differential_result.growth_differential is not None else 0.0
        inflation_diff = differential_result.inflation_differential if differential_result.inflation_differential is not None else 0.0
        
        # MacroDifferentialProvider entrega policy rates en porcentaje (%).
        # DecisionPipeline/EconomicFilter requiere tasas en formato decimal
        # para convertir correctamente el diferencial a bps.
        base_rate = (
            differential_result.base_rate / 100.0
            if differential_result.base_rate is not None
            else 0.0
        )
        quote_rate = (
            differential_result.quote_rate / 100.0
            if differential_result.quote_rate is not None
            else 0.0
        )
        
        return PipelineInputs(
            artifact=artifact,
            policy_differential=policy_diff,
            growth_differential=growth_diff,
            inflation_differential=inflation_diff,
            base_signal=0.0,
            quote_signal=0.0,
            base_rate=base_rate,
            quote_rate=quote_rate,
            global_regime="Neutral",
            base_policy="Neutral",
            quote_policy="Neutral",
            required_minimum_edge=REQUIRED_MINIMUM_EDGE_BPS,
            base_size=BASE_SIZE,
            current_exposure=0.0,
            max_exposure=MAX_EXPOSURE,
            historical_reliability=HISTORICAL_RELIABILITY,
            model_loaded=True,
            required_data_missing=(
                differential_result.status != MacroDataStatus.FULL
            ),
            derived_available_time=as_of,
            input_available_times=[as_of]
        )
