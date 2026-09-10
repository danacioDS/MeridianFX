import numpy as np
from ..config import MAX_POSITION_SIZE, MIN_EDGE_RATIO, MIN_CONFIDENCE


class EconomicFilter:
    """Aplica filtros económicos a la decisión."""
    
    @staticmethod
    def apply(prediction: dict, latest_data: dict = None) -> dict:
        """
        Aplica filtros económicos y retorna decisión final.
        
        Recibe:
            prediction: dict con direction, probability, expected_return, expected_volatility
        """
        direction = prediction.get('direction', 'UP')
        probability = prediction.get('probability', 0.5)
        expected_return = prediction.get('expected_return', 0.0)
        expected_volatility = prediction.get('expected_volatility', 0.0)
        
        # Edge ratio basado en probabilidad
        edge_ratio = (probability - 0.5) / 0.5
        edge_ratio = max(0, min(edge_ratio, 3.0))
        
        # Confidence basada en probabilidad
        confidence = (probability - 0.5) * 2
        confidence = max(0, min(confidence, 1.0))
        
        # Signal strength
        signal_strength = (edge_ratio / 3.0) * confidence
        
        # Actionable
        actionable = (edge_ratio >= MIN_EDGE_RATIO and confidence >= MIN_CONFIDENCE)
        
        # Position size
        position_size = 0 if not actionable else confidence * MAX_POSITION_SIZE
        
        # Net return = expected_return - costs (aprox 30%)
        net_return = expected_return * 0.7
        
        return {
            'direction': direction,
            'probability': probability,
            'expected_return': expected_return,
            'expected_volatility': expected_volatility,
            'actionable': actionable,
            'confidence': confidence,
            'signal_strength': signal_strength,
            'edge_ratio': edge_ratio,
            'net_return': net_return,
            'position_size': position_size
        }
