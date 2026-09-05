"""
Entrenamiento de modelos experimentales candidatos.
Usa exactamente el mismo pipeline evaluado: Logistic Regression + Sigmoid calibration.
"""

import joblib
import json
import os
from datetime import datetime

from backend.layer2.data.provider import DataProvider
from backend.layer2.features.technical import TechnicalFeatures

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator

# Candidatos aprobados por el Research Gate
CANDIDATES = [
    ("USD/BOB", 20),
    ("EUR/USD", 10),
]

DATA_PERIOD = "2y"
RANDOM_STATE = 42

dp = DataProvider()

print("=" * 80)
print("MERIDIANFX — ENTRENAMIENTO DE MODELOS EXPERIMENTALES")
print("=" * 80)
print(f"Candidatos: {len(CANDIDATES)}")
print("Modelo: Logistic Regression + Sigmoid calibration")
print("=" * 80)

for pair, horizon in CANDIDATES:
    print(f"\n🔄 Entrenando {pair} — {horizon}d")

    # Obtener datos
    result = dp.get_historical(pair, period=DATA_PERIOD)
    df = result["data"]
    df_feat = TechnicalFeatures.generate(df)
    feature_cols = TechnicalFeatures.get_feature_names()

    y_all = TechnicalFeatures.create_target(df_feat, forward_days=horizon)
    X_all = df_feat[feature_cols]

    valid = X_all.notna().all(axis=1) & y_all.notna()
    X = X_all.loc[valid].copy()
    y = y_all.loc[valid].copy().astype(int)

    print(f"  Muestras: {len(X)}")
    print(f"  Features: {X.shape[1]}")

    # Entrenar modelo con todos los datos disponibles
    model = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("logistic", LogisticRegression(
            max_iter=5000,
            random_state=RANDOM_STATE
        ))
    ])
    model.fit(X, y)

    # Calibración sigmoid
    calibrator = CalibratedClassifierCV(
        FrozenEstimator(model),
        method='sigmoid'
    )
    calibrator.fit(X, y)

    # Guardar modelos
    save_dir = f"models/experimental/{pair.replace('/', '_')}/h{horizon}"
    os.makedirs(save_dir, exist_ok=True)

    joblib.dump(model, f"{save_dir}/model.pkl")
    joblib.dump(calibrator, f"{save_dir}/calibrator.pkl")

    # Guardar metadata
    metadata = {
        "pair": pair,
        "horizon": horizon,
        "model_type": "logistic_regression",
        "calibration": "sigmoid",
        "features": feature_cols,
        "n_features": len(feature_cols),
        "n_samples": len(X),
        "feature_names": feature_cols,
        "training_date": datetime.now().isoformat(),
        "data_period": DATA_PERIOD,
        "random_state": RANDOM_STATE,
        "status": "EXPERIMENTAL",
        "research_protocol": "60/20/20",
        "purge": horizon,
        "notes": "Candidato aprobado por Research Gate para producción experimental"
    }

    with open(f"{save_dir}/metadata.json", "w") as f:
        json.dump(metadata, f, indent=2, default=str)

    print(f"  ✅ Modelo guardado en: {save_dir}")
    print(f"  📄 Metadata guardada")

print("\n" + "=" * 80)
print("✅ Entrenamiento completado")
print("=" * 80)
