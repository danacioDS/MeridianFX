"""
Real Research Gate — Layer 3 v5.0 §8

Evaluates models using real data and enforces strict criteria.
"""
from typing import Dict, Any, Optional
from layer3.evaluation.model_evaluator import ModelEvaluator


class RealResearchGate:
    """
    Research Gate with real data validation.
    
    Criteria:
    - DA > 0.52 (screening)
    - AUC > 0.55
    - Sharpe > 0.3 (screening)
    - MaxDD > -0.20
    """
    
    MIN_DA = 0.52
    MIN_AUC = 0.55
    MIN_SHARPE = 0.3
    MAX_DRAWDOWN = -0.20
    
    def __init__(self, data_provider=None):
        self.evaluator = ModelEvaluator(data_provider)
    
    def evaluate_and_validate(self, pair: str, model, model_id: str) -> Dict[str, Any]:
        """
        Evaluate a model and validate against Research Gate criteria.
        """
        # Run evaluation
        eval_result = self.evaluator.evaluate_xgboost(pair, model)
        
        if 'error' in eval_result:
            return {
                'model_id': model_id,
                'pair': pair,
                'status': 'REJECTED',
                'reason': eval_result['error'],
                'metrics': {}
            }
        
        metrics = eval_result.get('metrics', {})
        passed = True
        failures = []
        
        # Check criteria
        if metrics.get('DA', 0) < self.MIN_DA:
            passed = False
            failures.append(f"DA {metrics.get('DA', 0):.3f} < {self.MIN_DA}")
        
        if metrics.get('AUC', 0) < self.MIN_AUC:
            passed = False
            failures.append(f"AUC {metrics.get('AUC', 0):.3f} < {self.MIN_AUC}")
        
        if metrics.get('Sharpe', 0) < self.MIN_SHARPE:
            passed = False
            failures.append(f"Sharpe {metrics.get('Sharpe', 0):.3f} < {self.MIN_SHARPE}")
        
        if metrics.get('MaxDD', 0) < self.MAX_DRAWDOWN:
            passed = False
            failures.append(f"MaxDD {metrics.get('MaxDD', 0):.3f} < {self.MAX_DRAWDOWN}")
        
        return {
            'model_id': model_id,
            'pair': pair,
            'status': 'APPROVED' if passed else 'REJECTED',
            'reason': 'All criteria passed' if passed else f'Failed: {", ".join(failures)}',
            'metrics': metrics,
            'eval_result': eval_result
        }
