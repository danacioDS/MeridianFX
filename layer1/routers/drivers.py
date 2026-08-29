from fastapi import APIRouter, Path
from datetime import datetime
from ..models.responses import DriversResponse, ShapContribution, MacroRegime, Rag, RagSignal
import sys
import os

# Asegurar que layer2 está en el path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from layer2.engine import DecisionEngine
from layer2.data.macro.service import MacroService
from layer2.data.macro.transformer import MacroTransformer

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

# Inicializar MacroService
macro_service = MacroService()
macro_transformer = MacroTransformer()

router = APIRouter(prefix="/v1/fx", tags=["drivers"])

async def get_macro_regime(pair: str) -> MacroRegime:
    """Obtiene el régimen macro real desde FRED."""
    try:
        # Obtener datos macro (async - CON AWAIT)
        macro_data = await macro_service.get_macro_context()
        
        # Transformar a régimen usando to_regime
        regime = macro_transformer.to_regime(macro_data)
        
        return MacroRegime(
            risk=regime.get('risk', 'MODERATE'),
            policy=regime.get('policy', 'NEUTRAL'),
            growth=regime.get('growth', 'STABLE'),
            inflation=regime.get('inflation', 'STABLE')
        )
    except Exception as e:
        print(f"⚠️ Macro regime error: {e}")
        # Fallback a placeholder
        return MacroRegime(
            risk="MODERATE",
            policy="NEUTRAL",
            growth="STABLE",
            inflation="STABLE"
        )

def get_rag_signals(pair: str) -> Rag:
    """Obtiene señales RAG (LLM) - placeholder por ahora."""
    return Rag(
        fed=RagSignal(sentiment=0.0, expectation_gap=0.0),
        boj=RagSignal(sentiment=0.0, expectation_gap=0.0)
    )

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
    
    # Macro regime REAL desde FRED (async - CON AWAIT)
    macro_regime = await get_macro_regime(pair)
    
    # RAG (placeholder por ahora)
    rag = get_rag_signals(pair)
    
    # Narrative con macro context
    narrative = drivers_data.get('narrative', '')
    if not narrative:
        narrative = f"Top drivers: {', '.join([f'{d.feature} ({d.contribution:.3f})' for d in shap_list[:3]])}. " + \
                    f"Régimen macro: Riesgo={macro_regime.risk}, " + \
                    f"Política={macro_regime.policy}, " + \
                    f"Crecimiento={macro_regime.growth}, " + \
                    f"Inflación={macro_regime.inflation}."
    
    return DriversResponse(
        pair=pair,
        timestamp=datetime.now(),
        shap=shap_list,
        macro_regime=macro_regime,
        rag=rag,
        narrative=narrative,
        risks=[],
        event_sensitivity=[]
    )
