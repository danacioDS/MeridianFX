"""
Bridge entre Layer 2 (datos) y DecisionPipeline (decisión)
Reutiliza DecisionEngineAdapter para construir PredictionArtifact.
"""

from typing import Dict, Any
from datetime import datetime, timezone

from backend.src.meridian_fx.decision.pipeline import DecisionPipeline, PipelineInputs
from backend.src.meridian_fx.decision.contracts import PredictionArtifact

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


class PipelineBridge:
    """Conecta Layer 2 con el DecisionPipeline usando el adapter existente."""
    
    def __init__(self, pipeline: DecisionPipeline):
        self.pipeline = pipeline
        self.data_provider = DataProvider()
        self.engine = DecisionEngine()
        self.adapter = DecisionEngineAdapter(self.engine)
        self.macro_service = MacroService()
        self.macro_transformer = MacroTransformer()
    
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
        
        # 5. Determinar disponibilidad de datos macro
        base, quote = pair.split('/')
        
        # Por ahora, solo tenemos datos de EE.UU. (FRED).
        # La disponibilidad debe respetar la posición de USD en el par.
        # Esto evolucionará con MacroDifferentialProvider.
        usd_available = True

        base_available = base == "USD" and usd_available
        quote_available = quote == "USD" and usd_available

        if base_available and quote_available:
            status = MacroDataStatus.FULL
        elif base_available or quote_available:
            status = MacroDataStatus.PARTIAL
        else:
            status = MacroDataStatus.UNAVAILABLE

        macro_status = MacroDifferentialStatus(
            status=status,
            base_currency=base,
            quote_currency=quote,
            base_available=base_available,
            quote_available=quote_available,
            reason=(
                "Only USD macro data currently available (FRED). "
                "Quote/base-country macro differential cannot be calculated."
            ),
            policy_diff_status="UNAVAILABLE",
            growth_diff_status="UNAVAILABLE",
            rate_diff_status="UNAVAILABLE",
        )
        
        # 6. Construir PipelineInputs con fallback explícito
        inputs = self._build_inputs(artifact)
        
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
            "macro_data_status": macro_status.to_dict(),  # <-- Trazabilidad
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _build_inputs(self, artifact: PredictionArtifact) -> PipelineInputs:
        """Construye PipelineInputs usando el timestamp del artifact."""
        as_of = artifact.as_of
        
        return PipelineInputs(
            artifact=artifact,
            policy_differential=0.0,
            growth_differential=0.0,
            normalized_rate_differential=0.0,
            base_signal=0.0,
            quote_signal=0.0,
            base_rate=0.0,
            quote_rate=0.0,
            global_regime="Neutral",
            base_policy="Neutral",
            quote_policy="Neutral",
            required_minimum_edge=10.0,
            base_size=100_000.0,
            current_exposure=0.0,
            max_exposure=1_000_000.0,
            historical_reliability=0.5,
            model_loaded=True,
            required_data_missing=False,
            derived_available_time=as_of,
            input_available_times=[as_of]
        )
