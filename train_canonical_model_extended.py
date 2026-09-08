"""
Entrenamiento del modelo canónico de MeridianFX — Versión extendida
Candidato: LogisticRegression + 23 technical features + policy_diff
Período: 2020-2026 (máximo disponible) para incluir policy_diff negativo
"""

import json
import joblib
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from backend.layer2.data.provider import DataProvider
from backend.layer2.features.technical import TechnicalFeatures
from backend.layer2.data.sources.fred import FredDataSource
from backend.layer2.data.macro.service import MacroService
from backend.layer2.data.macro.differential_provider import MacroDifferentialProvider

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

import asyncio

print("=" * 70)
print("MERIDIANFX — ENTRENAMIENTO EXTENDIDO")
print("=" * 70)

# Configuración
PAIR = "EUR/USD"
HORIZON = 10
OUTPUT_DIR = "models/canonical"
PERIOD = "5y"

# Obtener datos
dp = DataProvider()
result = dp.get_historical(PAIR, period=PERIOD)
df = result["data"]
print(f"📥 Datos cargados: {len(df)} filas")
print(f"   Período: {df.index.min()} → {df.index.max()}")

# Generar features técnicas
df_feat = TechnicalFeatures.generate(df)
technical_cols = TechnicalFeatures.get_feature_names()
print(f"📈 Features técnicas: {len(technical_cols)}")

# Obtener policy_diff PIT para todo el período
print("\n📊 Calculando policy_diff PIT...")

async def get_policy_diff_extended():
    price_dates = pd.DatetimeIndex(df_feat.index)
    start_date = (price_dates.min() - pd.Timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = price_dates.max().strftime("%Y-%m-%d")
    
    macro_service = MacroService()
    
    eur = await macro_service.get_historical_policy_rate("EUR", start_date, end_date)
    usd = await macro_service.get_historical_policy_rate("USD", start_date, end_date)
    
    if eur.empty or usd.empty:
        print("⚠️ No se pudieron obtener series históricas completas. Usando fallback.")
        return pd.Series(-0.345, index=price_dates)
    
    policy_diff = MacroDifferentialProvider.calculate_historical(
        base_currency="EUR",
        quote_currency="USD",
        base_series=eur,
        quote_series=usd,
        price_dates=price_dates,
    )
    
    return policy_diff

# Ejecutar async
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
policy_diff = loop.run_until_complete(get_policy_diff_extended())
loop.close()

# Alinear y añadir a df_feat
policy_aligned = policy_diff.reindex(df_feat.index)
df_feat["policy_diff"] = policy_aligned

# Verificar cobertura
valid_policy = df_feat["policy_diff"].notna()
print(f"   Policy_diff disponible: {valid_policy.sum()}/{len(df_feat)} filas")
print(f"   Rango policy_diff: {df_feat['policy_diff'].min():.4f} → {df_feat['policy_diff'].max():.4f}")
print(f"   Mean policy_diff: {df_feat['policy_diff'].mean():.4f}")
print(f"   Std policy_diff: {df_feat['policy_diff'].std():.4f}")

# Construir dataset completo
feature_cols = technical_cols + ["policy_diff"]
X_all = df_feat[feature_cols]
y_all = TechnicalFeatures.create_target(df_feat, forward_days=HORIZON)

valid = X_all.notna().all(axis=1) & y_all.notna()
X = X_all.loc[valid].copy()
y = y_all.loc[valid].copy()

print(f"\n📊 Dataset final: {len(X)} filas, {X.shape[1]} features")
print(f"   Primera fecha: {X.index[0]}")
print(f"   Última fecha: {X.index[-1]}")

# Verificar rango de policy_diff en entrenamiento
policy_range = X["policy_diff"].describe()
print(f"\n📊 Policy_diff en entrenamiento:")
print(policy_range)

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

# Verificar scaler para policy_diff
scaler = model.named_steps["scaler"]
policy_idx = X.columns.get_loc("policy_diff")
print(f"\n📊 Scaler para policy_diff:")
print(f"   Mean: {scaler.mean_[policy_idx]:.6f}")
print(f"   Std:  {scaler.scale_[policy_idx]:.6f}")

# Calcular z-score del valor actual
current_policy = -0.345
z_score = (current_policy - scaler.mean_[policy_idx]) / scaler.scale_[policy_idx]
print(f"   Current policy_diff: {current_policy:.6f}")
print(f"   Z-score: {z_score:.4f}")
print(f"   ⚠️ Z-score > 3: {'✅' if abs(z_score) < 3 else '🔴 Extrapolación'}")

# Guardar artefacto
os.makedirs(OUTPUT_DIR, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
artifact_path = f"{OUTPUT_DIR}/logistic_24_extended_{timestamp}.joblib"

artifact = {
    "model": model,
    "feature_names": X.columns.tolist(),
    "horizon": HORIZON,
    "pair": PAIR,
    "timestamp": timestamp,
    "version": "2.0.0",
    "training_period": {
        "start": X.index[0].strftime("%Y-%m-%d"),
        "end": X.index[-1].strftime("%Y-%m-%d"),
        "n_samples": len(X),
    },
    "policy_diff_stats": {
        "mean": float(X["policy_diff"].mean()),
        "std": float(X["policy_diff"].std()),
        "min": float(X["policy_diff"].min()),
        "max": float(X["policy_diff"].max()),
        "current_z_score": float(z_score),
    },
}

joblib.dump(artifact, artifact_path)
print(f"\n✅ Modelo guardado en {artifact_path}")

# Guardar metadata
metadata = {
    "model_type": "LogisticRegression",
    "features": X.columns.tolist(),
    "n_features": len(X.columns),
    "horizon": HORIZON,
    "pair": PAIR,
    "training_date": timestamp,
    "version": "2.0.0",
    "training_period": {
        "start": X.index[0].strftime("%Y-%m-%d"),
        "end": X.index[-1].strftime("%Y-%m-%d"),
        "n_samples": len(X),
    },
    "policy_diff_stats": {
        "mean": float(X["policy_diff"].mean()),
        "std": float(X["policy_diff"].std()),
        "min": float(X["policy_diff"].min()),
        "max": float(X["policy_diff"].max()),
        "current_z_score": float(z_score),
    },
}

with open(f"{OUTPUT_DIR}/metadata_extended_{timestamp}.json", "w") as f:
    json.dump(metadata, f, indent=2)

print(f"✅ Metadata guardada en {OUTPUT_DIR}/metadata_extended_{timestamp}.json")
print("\n" + "=" * 70)
print("✅ ENTRENAMIENTO EXTENDIDO COMPLETADO")
