from fastapi import APIRouter, Path
from datetime import datetime
from ..models.responses import DriversResponse, ShapContribution, MacroRegime, Rag, RagSignal
import sys
import os

# Asegurar que layer2 está en el path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from layer2.engine import DecisionEngine

# Crear engine y asegurar que carga los modelos
def get_engine():
    """Obtiene el engine y asegura que los modelos estén cargados."""
    engine = DecisionEngine()
    # Forzar carga de modelos si no están cargados
    if not engine.is_trained and engine.registry:
        active_xgb = engine.registry.get_active('USD/JPY', 'xgboost')
        if active_xgb:
            from layer2.models.xgboost_model import XGBoostModel
            engine.xgb_model = XGBoostModel(active_xgb['path'])
            if engine.xgb_model.model is not None:
                engine.is_trained = True
                # Inicializar SHAP
                try:
                    from layer2.data.provider import DataProvider
                    from layer2.features.technical import TechnicalFeatures
                    from layer2.explainers.shap_explainer import SHAPExplainer
                    
                    data_provider = DataProvider()
                    result = data_provider.get_historical('USD/JPY', period='1y')
                    df = result['data']
                    df_feat = TechnicalFeatures.generate(df)
                    feature_cols = TechnicalFeatures.get_feature_names()
                    X_background = df_feat[feature_cols].dropna()
                    
                    if len(X_background) > 0:
                        engine.shap_explainer = SHAPExplainer(
                            engine.xgb_model.model,
                            engine.xgb_model.feature_names,
                            X_background
                        )
                except Exception as e:
                    print(f"⚠️ SHAP init error: {e}")
    return engine

_engine = get_engine()

router = APIRouter(prefix="/v1/fx", tags=["drivers"])

@router.get("/{pair:path}/drivers", response_model=DriversResponse)
async def get_drivers(
    pair: str = Path(..., description="Currency pair (e.g., USD/JPY)")
):
    """Obtener drivers y explicación SHAP para un par."""
    # Asegurar que el engine está cargado
    engine = get_engine()
    
    # Obtener drivers con SHAP de Layer 2
    drivers_data = engine.get_drivers(pair)
    
    shap_contributions = drivers_data.get('shap', [])
    
    # Convertir a formato ShapContribution
    shap_list = []
    for i, d in enumerate(shap_contributions[:10]):
        shap_list.append(
            ShapContribution(
                rank=i+1,
                feature=d.get('feature', 'unknown'),
                contribution=d.get('contribution', 0.0)
            )
        )
    
    # Macro regime (placeholder)
    macro_regime = MacroRegime(
        risk="MODERATE",
        growth="STABLE",
        policy="NEUTRAL",
        inflation="STABLE"
    )
    
    # RAG (placeholder)
    rag = Rag(
        fed=RagSignal(sentiment=0.0, expectation_gap=0.0),
        boj=RagSignal(sentiment=0.0, expectation_gap=0.0)
    )
    
    return DriversResponse(
        pair=pair,
        timestamp=datetime.now(),
        shap=shap_list,
        macro_regime=macro_regime,
        rag=rag,
        narrative=drivers_data.get('narrative', 'No narrative available'),
        risks=[],
        event_sensitivity=[]
    )
