"""
Model Comparison Router — Compara XGBoost, Logistic y Ensemble.
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from layer2.engine import DecisionEngine
from layer1.utils.pair_normalizer import normalize_pair
from layer3.evaluation.walk_forward import WalkForwardEvaluator

router = APIRouter(prefix="/v1/fx", tags=["model_comparison"])

# Cache de resultados de comparación
_comparison_cache = {}

def get_comparison(
    pair: str,
    horizon: int = 5,
    initial_train_years: int = 3
) -> dict:
    """Obtiene comparación de modelos con walk-forward."""

    normalized_pair = normalize_pair(pair)

    cache_key = (
        f"{normalized_pair}_{horizon}_{initial_train_years}"
    )

    if cache_key in _comparison_cache:
        return _comparison_cache[cache_key]

    engine = DecisionEngine()
    evaluator = WalkForwardEvaluator(
        data_provider=engine.data_provider
    )

    results = {}
    models = {}

    # ---------------------------------------------------------
    # XGBoost
    # ---------------------------------------------------------

    xgb_model = engine._get_model_for_pair(
        normalized_pair,
        "xgboost"
    )

    if xgb_model is not None:

        result = evaluator.evaluate_expanding(
            normalized_pair,
            xgb_model,
            horizon=horizon,
            initial_train_years=initial_train_years,
            test_years=1,
            step_years=1
        )

        agg = result.get("aggregate", {})

        results["xgboost"] = {
            "sharpe": agg.get("mean_Sharpe", 0),
            "profit_factor": agg.get(
                "mean_ProfitFactor", 0
            ),
            "da": agg.get("mean_DA", 0),
            "auc": agg.get("mean_AUC", 0),
            "net_return": agg.get(
                "mean_NetReturn", 0
            ),
            "n_windows": result.get(
                "n_windows", 0
            )
        }

        models["xgboost"] = {
            "available": True
        }

    # ---------------------------------------------------------
    # Logistic
    # ---------------------------------------------------------

    logistic_model = engine._get_model_for_pair(
        normalized_pair,
        "logistic"
    )

    if logistic_model is not None:

        result = evaluator.evaluate_expanding(
            normalized_pair,
            logistic_model,
            horizon=horizon,
            initial_train_years=initial_train_years,
            test_years=1,
            step_years=1
        )

        agg = result.get("aggregate", {})

        results["logistic"] = {
            "sharpe": agg.get("mean_Sharpe", 0),
            "profit_factor": agg.get(
                "mean_ProfitFactor", 0
            ),
            "da": agg.get("mean_DA", 0),
            "auc": agg.get("mean_AUC", 0),
            "net_return": agg.get(
                "mean_NetReturn", 0
            ),
            "n_windows": result.get(
                "n_windows", 0
            )
        }

        models["logistic"] = {
            "available": True
        }

    # ---------------------------------------------------------
    # Ensemble
    # ---------------------------------------------------------
    #
    # NO presentar todavía como evaluación real.
    # El ensemble necesita ser evaluado dentro del
    # walk-forward, no promediando métricas.
    #

    if xgb_model is not None and logistic_model is not None:

        models["ensemble"] = {
            "available": False,
            "evaluation": "not_implemented"
        }

    # ---------------------------------------------------------
    # Best model
    # ---------------------------------------------------------

    best_model = (
        max(
            results.items(),
            key=lambda x: x[1].get("sharpe", 0)
        )[0]
        if results
        else None
    )

    result = {
        "pair": normalized_pair,
        "horizon": horizon,
        "initial_train_years": initial_train_years,
        "results": results,
        "models": models,
        "best_model": best_model,
        "timestamp": datetime.now().isoformat()
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
