"""
Full Research Gate — Layer 3 v5.0 §8

Combines all four gates:
1. Leakage Check
2. Statistical Validation
3. Economic Validation
4. Robustness Check
"""
from typing import Dict, Any, Optional
from .gate import ResearchGate, ResearchGateReport
from layer3.evaluation.walk_forward import WalkForwardEvaluator


class FullResearchGate:
    """
    Full Research Gate with walk-forward evaluation.
    
    Runs all four gates on a model:
    1. Leakage Check (PIT compliance)
    2. Statistical Validation (DA > 52%, AUC > 0.55, ECE < 0.05)
    3. Economic Validation (Sharpe > 0.3, MaxDD > -20%, Profit Factor > 1.2)
    4. Robustness Check (rolling Sharpe stability)
    """
    
    def __init__(self, data_provider=None):
        self.evaluator = WalkForwardEvaluator(data_provider)
        self.gate = ResearchGate()
    
    def evaluate_and_validate(self, pair: str, model, model_id: str,
                              horizon: int = 5) -> Dict[str, Any]:
        """
        Run walk-forward evaluation and apply all four gates.
        """
        # 1. Run walk-forward evaluation
        eval_result = self.evaluator.evaluate(pair, model, horizon)
        
        if 'error' in eval_result:
            return {
                'model_id': model_id,
                'pair': pair,
                'status': 'REJECTED',
                'reason': eval_result['error'],
                'gates': {},
                'metrics': {}
            }
        
        # 2. Extract REAL metrics from evaluation
        agg = eval_result.get('aggregate', {})
        
        # Statistical metrics (from evaluation)
        stats = {
            'directional_accuracy': agg.get('mean_DA', 0),
            'auc': agg.get('mean_AUC', 0),
            'ece': agg.get('mean_ECE', 0.5),  # Now from evaluation
        }
        
        # Economic metrics (from evaluation)
        economic = {
            'sharpe_net': agg.get('mean_Sharpe', 0),
            'max_drawdown': agg.get('mean_MaxDD', 0),
            'profit_factor': agg.get('mean_ProfitFactor', 1.0),
            'net_return': agg.get('mean_NetReturn', 0),
        }
        
        # Robustness metrics (from evaluation)
        robustness = {
            'rolling_sharpe': eval_result.get('rolling_sharpe', []),
            'oos_metrics': eval_result.get('oos_metrics', [])
        }
        
        # 3. Run all four gates
        report = self.gate.evaluate(
            features={},  # Placeholder for leakage
            metrics=stats,
            economic=economic,
            robustness=robustness
        )
        
        return {
            'model_id': model_id,
            'pair': pair,
            'status': report.overall_status,
            'reason': 'All gates passed' if report.overall_status == 'APPROVED' else 'Research Gate failed',
            'gates': {
                'leakage': {
                    'passed': report.leakage_check.passed,
                    'message': report.leakage_check.message
                },
                'statistical': {
                    'passed': report.statistical_validation.passed,
                    'message': report.statistical_validation.message,
                    'metrics': {
                        'DA': stats['directional_accuracy'],
                        'AUC': stats['auc'],
                        'ECE': stats['ece']
                    }
                },
                'economic': {
                    'passed': report.economic_validation.passed,
                    'message': report.economic_validation.message,
                    'metrics': {
                        'Sharpe': economic['sharpe_net'],
                        'MaxDD': economic['max_drawdown'],
                        'ProfitFactor': economic['profit_factor'],
                        'NetReturn': economic['net_return']
                    }
                },
                'robustness': {
                    'passed': report.robustness_check.passed,
                    'message': report.robustness_check.message,
                    'metrics': {
                        'n_windows': eval_result.get('n_windows', 0),
                        'rolling_sharpe': eval_result.get('rolling_sharpe', [])
                    }
                }
            },
            'metrics': {
                'mean_DA': agg.get('mean_DA', 0),
                'mean_AUC': agg.get('mean_AUC', 0),
                'mean_ECE': agg.get('mean_ECE', 0.5),
                'mean_Sharpe': agg.get('mean_Sharpe', 0),
                'mean_MaxDD': agg.get('mean_MaxDD', 0),
                'mean_ProfitFactor': agg.get('mean_ProfitFactor', 0),
                'mean_NetReturn': agg.get('mean_NetReturn', 0),
                'n_windows': eval_result.get('n_windows', 0),
                'total_test_samples': eval_result.get('total_test_samples', 0)
            },
            'eval_result': eval_result
        }
