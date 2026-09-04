"""
Bridge entre Layer 2 (datos) y DecisionPipeline (decisión)
"""

from typing import Optional
from src.meridian_fx.decision.pipeline import DecisionPipeline, PipelineInputs
from src.meridian_fx.decision.contracts import PredictionArtifact
from layer2.data.provider import DataProvider
from layer2.features.technical import TechnicalFeatures

class PipelineBridge:
    """Conecta Layer 2 con el DecisionPipeline"""
    
    def __init__(self, pipeline: DecisionPipeline):
        self.pipeline = pipeline
        self.data_provider = DataProvider()
    
    def evaluate_pair(self, pair: str) -> dict:
        """Evalúa un par usando el pipeline"""
        # 1. Obtener datos
        data = self.data_provider.get_historical(pair, period='1y')
        
        # 2. Generar features
        features = TechnicalFeatures.generate(data['data'])
        
        # 3. Crear PredictionArtifact
        artifact = self._create_artifact(pair, features)
        
        # 4. Ejecutar pipeline
        inputs = self._build_inputs(artifact, features)
        result = self.pipeline.build(inputs)
        
        # 5. Retornar decisión
        return result.decision.model_dump()
    
    def _create_artifact(self, pair: str, features) -> PredictionArtifact:
        # Implementar según contract L3 §11.2
        pass
    
    def _build_inputs(self, artifact, features) -> PipelineInputs:
        # Implementar según contract L4 §7
        pass
