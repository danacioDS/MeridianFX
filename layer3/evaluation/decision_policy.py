"""
Decision Policy — Prueba de diferentes thresholds de probabilidad.

Evalúa cómo afecta la decisión LONG/FLAT/SHORT al rendimiento.
"""
import numpy as np
from typing import Dict, List, Tuple


class DecisionPolicyEvaluator:
    """
    Evalúa diferentes políticas de decisión basadas en umbrales de probabilidad.
    """
    
    @staticmethod
    def evaluate_policy(y_proba: np.ndarray, future_returns: np.ndarray,
                        threshold_up: float = 0.6, threshold_down: float = 0.4) -> Dict:
        """
        Evalúa una política con umbrales.
        
        Args:
            y_proba: Probabilidades de predicción (0-1)
            future_returns: Retornos futuros del horizonte
            threshold_up: Umbral para LONG (por encima)
            threshold_down: Umbral para SHORT (por debajo)
        
        Returns:
            Métricas de la política
        """
        from layer3.evaluation.benchmarks import BenchmarkEvaluator
        
        # Decisión: LONG si proba > threshold_up, SHORT si proba < threshold_down, FLAT en medio
        positions = np.zeros_like(y_proba)
        positions[y_proba > threshold_up] = 1.0
        positions[y_proba < threshold_down] = -1.0
        
        strategy_returns = positions * future_returns
        
        benchmark = BenchmarkEvaluator()
        metrics = benchmark.evaluate_strategy(strategy_returns, horizon=5)
        
        return {
            'threshold_up': threshold_up,
            'threshold_down': threshold_down,
            'positions': positions,
            'n_long': int(np.sum(positions == 1)),
            'n_short': int(np.sum(positions == -1)),
            'n_flat': int(np.sum(positions == 0)),
            'metrics': metrics
        }
    
    @staticmethod
    def grid_search(y_proba: np.ndarray, future_returns: np.ndarray) -> List[Dict]:
        """
        Búsqueda de grid para encontrar mejores umbrales.
        """
        results = []
        
        for up in [0.5, 0.55, 0.6, 0.65, 0.7]:
            for down in [0.5, 0.45, 0.4, 0.35, 0.3]:
                if up <= down:
                    continue
                result = DecisionPolicyEvaluator.evaluate_policy(
                    y_proba, future_returns, up, down
                )
                result['params'] = (up, down)
                results.append(result)
        
        return results
