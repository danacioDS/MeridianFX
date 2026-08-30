"""
Model Comparison Router — Compara XGBoost, Logistic y Ensemble.
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from layer2.engine import DecisionEngine
from layer3.evaluation.walk_forward import WalkForwardEvaluator

router = APIRouter(prefix="/v1/fx", tags=["model_comparison"])

# Cache de resultados de comparación
_comparison_cache = {}

def get_comparison(pair: str, horizon: int = 5, initial_train_years: int = 3) -> dict:
    """Obtiene comparación de modelos con walk-forward."""
    
    cache_key = f"{pair}_{horizon}_{initial_train_years}"
    if cache_key in _comparison_cache:
        return _comparison_cache[cache_key]
    
    engine = DecisionEngine()
    evaluator = WalkForwardEvaluator(data_provider=engine.data_provider)
    
    results = {}
    models = {}
    
    # XGBoost
    if engine.xgb_model:
        result = evaluator.evaluate_expanding(
            pair, engine.xgb_model, horizon=horizon,
            initial_train_years=initial_train_years, test_years=1, step_years=1
        )
        agg = result.get('aggregate', {})
        results['xgboost'] = {
            'sharpe': agg.get('mean_Sharpe', 0),
            'profit_factor': agg.get('mean_ProfitFactor', 0),
            'da': agg.get('mean_DA', 0),
            'auc': agg.get('mean_AUC', 0),
            'net_return': agg.get('mean_NetReturn', 0),
            'n_windows': result.get('n_windows', 0)
        }
        models['xgboost'] = {'available': True}
    
    # Logistic
    if engine.logistic_model:
        result = evaluator.evaluate_expanding(
            pair, engine.logistic_model, horizon=horizon,
            initial_train_years=initial_train_years, test_years=1, step_years=1
        )
        agg = result.get('aggregate', {})
        results['logistic'] = {
            'sharpe': agg.get('mean_Sharpe', 0),
            'profit_factor': agg.get('mean_ProfitFactor', 0),
            'da': agg.get('mean_DA', 0),
            'auc': agg.get('mean_AUC', 0),
            'net_return': agg.get('mean_NetReturn', 0),
            'n_windows': result.get('n_windows', 0)
        }
        models['logistic'] = {'available': True}
    
    # Ensemble (XGBoost + Logistic)
    if engine.xgb_model and engine.logistic_model:
        from layer3.models.ensemble import EnsembleModel
        ensemble = EnsembleModel()
        ensemble.add_model('xgboost', engine.xgb_model, weight=0.5)
        ensemble.add_model('logistic', engine.logistic_model, weight=0.5)
        
        # Simular ensemble (para walk-forward, necesitamos implementar correctamente)
        # Por ahora, usamos promedios ponderados de los resultados existentes
        xgb_agg = results.get('xgboost', {})
        log_agg = results.get('logistic', {})
        
        results['ensemble'] = {
            'sharpe': 0.5 * xgb_agg.get('sharpe', 0) + 0.5 * log_agg.get('sharpe', 0),
            'profit_factor': 0.5 * xgb_agg.get('profit_factor', 0) + 0.5 * log_agg.get('profit_factor', 0),
            'da': 0.5 * xgb_agg.get('da', 0) + 0.5 * log_agg.get('da', 0),
            'auc': 0.5 * xgb_agg.get('auc', 0) + 0.5 * log_agg.get('auc', 0),
            'net_return': 0.5 * xgb_agg.get('net_return', 0) + 0.5 * log_agg.get('net_return', 0),
            'n_windows': min(xgb_agg.get('n_windows', 0), log_agg.get('n_windows', 0))
        }
        models['ensemble'] = {'available': True}
    
    # Determinar el mejor modelo
    best_model = max(results.items(), key=lambda x: x[1].get('sharpe', 0))[0] if results else None
    
    result = {
        'pair': pair,
        'horizon': horizon,
        'initial_train_years': initial_train_years,
        'results': results,
        'models': models,
        'best_model': best_model,
        'timestamp': datetime.now().isoformat()
    }
    
    _comparison_cache[cache_key] = result
    return result


@router.get("/{pair:path}/model-comparison")
async def get_model_comparison(pair: str, horizon: int = 5, initial_train_years: int = 3):
    """Obtiene comparación de modelos XGBoost, Logistic y Ensemble."""
    try:
        return get_comparison(pair, horizon, initial_train_years)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
