"""
Script para entrenar modelos XGBoost para todos los pares.
"""
from backend.layer2.models.xgboost_model import XGBoostModel
from backend.layer2.data.provider import DataProvider
from backend.layer2.features.technical import TechnicalFeatures
from backend.layer2.models.registry import ModelRegistry

data_provider = DataProvider()
registry = ModelRegistry()

pairs = ['USD/CNY', 'USD/MXN', 'USD/BRL', 'USD/ARS', 'USD/BOB', 'USD/CHF']

for pair in pairs:
    try:
        print(f'🔄 Entrenando {pair}...')
        result = data_provider.get_historical(pair, period='2y')
        df = result['data']
        df_feat = TechnicalFeatures.generate(df)
        feature_cols = TechnicalFeatures.get_feature_names()
        y = TechnicalFeatures.create_target(df_feat)
        X = df_feat[feature_cols]

        # Eliminar filas con features incompletas o sin horizonte futuro válido.
        valid = X.notna().all(axis=1) & y.notna()

        X = X.loc[valid]
        y = y.loc[valid].astype(int)

        if len(X) < 50:
            print(f'⚠️ Datos insuficientes para {pair}: {len(X)} muestras')
            continue
        
        model = XGBoostModel()
        metrics = model.train(X, y)
        
        # Guardar el modelo
        safe_pair = pair.replace("/", "_")
        path = f'models/xgboost_{safe_pair}_v1.0.pkl'
        model.save(path)
        
        # Registrar en el registry
        registry.register(pair, 'xgboost', 'v1.0', metrics, path)
        print(f'✅ {pair} entrenado y registrado!')
        print(f'   AUC: {metrics.get("auc", 0):.4f}, Accuracy: {metrics.get("accuracy", 0):.4f}')
        
    except Exception as e:
        print(f'❌ Error con {pair}: {e}')
