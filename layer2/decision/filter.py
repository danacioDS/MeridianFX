import numpy as np
from ..config import MAX_POSITION_SIZE, MIN_EDGE_RATIO, MIN_CONFIDENCE

class EconomicFilter:
    """Aplica filtros económicos a la decisión."""
    
    @staticmethod
    def apply(prediction: dict, latest_data: dict = None) -> dict:
        """Aplica filtros económicos y retorna decisión final."""
        direction = prediction.get('direction', 'UP')
        probability = prediction.get('probability', 0.5)
        
        # Cálculo de edge ratio (simplificado)
        edge_ratio = (probability - 0.5) / 0.5  # Normalizado
        edge_ratio = max(0, min(edge_ratio, 3.0))  # Entre 0 y 3
        
        # Confianza basada en probabilidad
        confidence = (probability - 0.5) * 2  # 0.5→0, 1.0→1
        confidence = max(0, min(confidence, 1.0))
        
        # Señal basada en edge y confianza
        signal_strength = (edge_ratio / 3.0) * confidence
        
        # Actionable: edge suficiente y confianza suficiente
        actionable = (edge_ratio >= MIN_EDGE_RATIO and confidence >= MIN_CONFIDENCE)
        
        # Position size: proporcional a la confianza
        position_size = 0 if not actionable else confidence * MAX_POSITION_SIZE
        
        # Expected return (simplificado)
        expected_return = (probability - 0.5) * 0.02  # 2% max
        expected_return = expected_return if direction == "UP" else -expected_return
        
        return {
            'direction': direction,
            'probability': probability,
            'expected_return': expected_return,
            'expected_volatility': 0.12,  # Valor por defecto
            'actionable': actionable,
            'confidence': confidence,
            'signal_strength': signal_strength,
            'edge_ratio': edge_ratio,
            'net_return': expected_return * 0.7,  # Net = Gross - costs
            'position_size': position_size
        }
