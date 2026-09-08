"""
Entrenamiento del modelo canónico de MeridianFX
Candidato: LogisticRegression + 23 technical features + policy_diff
"""

import pandas as pd
import numpy as np
import json
import joblib
import os
from datetime import datetime

from backend.layer2.data.provider import DataProvider
from backend.layer2.features.technical import TechnicalFeatures
from backend.layer2.data.sources.fred import FredDataSource

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

# Configuración
PAIR = "EUR/USD"
HORIZON = 10
OUTPUT_DIR = "models/canonical"

# Obtener datos
dp = DataProvider()
result = dp.get_historical(PAIR, period="4y")
df = result["data"]

# Generar features
df_feat = TechnicalFeatures.generate(df)
technical_cols = TechnicalFeatures.get_feature_names()

# Construir policy_diff PIT
from research_walkforward_head_to_head import prepare_dataset
X_tech, y_tech, X_macro, y_macro, tech_cols, macro_cols = prepare_dataset(df)

# Usar el dataset completo (sin split temporal)
X = X_macro
y = y_macro

print(f"Dataset: {len(X)} filas, {X.shape[1]} features")

# Entrenar modelo
model = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
    ("model", LogisticRegression(
        C=1.0,
        max_iter=1000,
        random_state=42,
        class_weight="balanced",
    )),
])

model.fit(X, y)

# Guardar artefacto
os.makedirs(OUTPUT_DIR, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
artifact_path = f"{OUTPUT_DIR}/logistic_24_{timestamp}.joblib"

artifact = {
    "model": model,
    "feature_names": X.columns.tolist(),
    "horizon": HORIZON,
    "pair": PAIR,
    "timestamp": timestamp,
    "version": "1.0.0",
}

joblib.dump(artifact, artifact_path)
print(f"✅ Modelo guardado en {artifact_path}")

# Guardar también los metadatos
metadata = {
    "model_type": "LogisticRegression",
    "features": X.columns.tolist(),
    "n_features": len(X.columns),
    "horizon": HORIZON,
    "pair": PAIR,
    "training_date": timestamp,
    "version": "1.0.0",
}

with open(f"{OUTPUT_DIR}/metadata_{timestamp}.json", "w") as f:
    json.dump(metadata, f, indent=2)

print("✅ Metadata guardada")
