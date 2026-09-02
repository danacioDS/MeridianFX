"""
Real Experiments — Layer 3 v5.0 §3

Runs sequential experiments E0-E7 with real data evaluation.
"""
from typing import Dict, Any
from layer3.evaluation.walk_forward import WalkForwardEvaluator


class RealExperimentRunner:
    """
    Runs experiments E0-E7 with real walk-forward evaluation.
    
    Each experiment returns real metrics from data, not placeholders.
    """
    
    def __init__(self, data_provider=None):
        self.evaluator = WalkForwardEvaluator(data_provider)
        self.results = {}
    
    def _evaluate_model(self, pair: str, model, experiment_id: str) -> Dict:
        """Evaluate a model with walk-forward backtesting."""
        result = self.evaluator.evaluate(pair, model)
        
        if 'error' in result:
            return {
                'experiment': experiment_id,
                'status': 'ERROR',
                'error': result['error'],
                'metrics': {}
            }
        
        agg = result.get('aggregate', {})
        return {
            'experiment': experiment_id,
            'status': 'COMPLETED',
            'metrics': {
                'DA': agg.get('mean_DA', 0),
                'AUC': agg.get('mean_AUC', 0),
                'Sharpe': agg.get('mean_Sharpe', 0),
                'MaxDD': agg.get('mean_MaxDD', 0),
            },
            'n_windows': result.get('n_windows', 0),
            'windows': result.get('windows', [])
        }
    
    def run_all(self, pair: str, models: Dict[str, Any]) -> Dict[str, Dict]:
        """
        Run all experiments E0-E7 with the provided models.
        
        Args:
            pair: Currency pair
            models: Dict mapping experiment_id to model
        """
        results = {}
        
        for exp_id, model in models.items():
            print(f"Running {exp_id}...")
            results[exp_id] = self._evaluate_model(pair, model, exp_id)
        
        self.results[pair] = results
        return results
    
    def summary(self, pair: str) -> Dict:
        """Get summary of all experiments for a pair."""
        if pair not in self.results:
            return {}
        
        summary = {}
        for exp_id, result in self.results[pair].items():
            metrics = result.get('metrics', {})
            summary[exp_id] = {
                'DA': metrics.get('DA', 0),
                'Sharpe': metrics.get('Sharpe', 0),
                'AUC': metrics.get('AUC', 0),
                'MaxDD': metrics.get('MaxDD', 0),
                'n_windows': result.get('n_windows', 0)
            }
        
        return summary
