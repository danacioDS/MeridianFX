"""
Entrenamiento de modelos Logistic_24 para múltiples pares
Mismo pipeline: 23 features técnicas + policy_diff PIT
"""

import json
import joblib
import os
import pandas as pd
import numpy as np
from datetime import datetime
import asyncio

from backend.layer2.data.provider import DataProvider
from backend.layer2.features.technical import TechnicalFeatures
from backend.layer2.data.macro.service import MacroService
from backend.layer2.data.macro.differential_provider import MacroDifferentialProvider

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

print("=" * 70)
print("MERIDIANFX — ENTRENAMIENTO MULTI-PARES")
print("=" * 70)

# Configuración
PAIRS = [
    "USD/CHF",
    "USD/BOB",
    "USD/MXN",
    "USD/CNY",
]
HORIZON = 10
OUTPUT_DIR = "models/canonical"
PERIOD = "4y"

dp = DataProvider()
macro_service = MacroService()

async def get_policy_diff_for_pair(pair, price_dates):
    """Obtiene policy_diff PIT para un par específico."""
    base, quote = pair.split('/')
    
    start_date = (price_dates.min() - pd.Timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = price_dates.max().strftime("%Y-%m-%d")
    
    # Obtener policy rates históricos
    # Por ahora solo USD y EUR tienen históricos reales
    # Para otros pares usamos el mismo policy_diff (USD - EUR)
    if base == "USD" and quote == "CHF":
        # USD/CHF: usar USD - CHF (CHF ≈ USD)
        # Por simplicidad, usamos USD - EUR como proxy
        eur = await macro_service.get_historical_policy_rate("EUR", start_date, end_date)
        usd = await macro_service.get_historical_policy_rate("USD", start_date, end_date)
        
        if eur.empty or usd.empty:
            return pd.Series(0.345, index=price_dates)
        
        policy_diff = MacroDifferentialProvider.calculate_historical(
            base_currency="USD",
            quote_currency="EUR",
            base_series=usd,
            quote_series=eur,
            price_dates=price_dates,
        )
        return policy_diff
    
    # Para otros pares, usar policy_diff constante por ahora
    # (en producción, se obtendría de fuentes específicas)
    print(f"   ⚠️ {pair}: usando policy_diff constante (0.345)")
    return pd.Series(0.345, index=price_dates)

def train_model(pair, df, policy_diff):
    """Entrena modelo Logistic_24 para un par."""
    print(f"\n📊 Entrenando {pair}...")
    
    # Generar features técnicas
    df_feat = TechnicalFeatures.generate(df)
    technical_cols = TechnicalFeatures.get_feature_names()
    
    # Añadir policy_diff
    policy_aligned = policy_diff.reindex(df_feat.index)
    df_feat["policy_diff"] = policy_aligned
    
    # Construir dataset
    feature_cols = technical_cols + ["policy_diff"]
    y_all = TechnicalFeatures.create_target(df_feat, forward_days=HORIZON)
    
    X_all = df_feat[feature_cols]
    valid = X_all.notna().all(axis=1) & y_all.notna()
    X = X_all.loc[valid].copy()
    y = y_all.loc[valid].copy()
    
    if len(X) < 100:
        print(f"   ⚠️ {pair}: muestra insuficiente ({len(X)} filas)")
        return None
    
    print(f"   Filas: {len(X)}, Features: {X.shape[1]}")
    
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
    
    # Estadísticas
    scaler = model.named_steps["scaler"]
    policy_idx = X.columns.get_loc("policy_diff")
    
    print(f"   Policy_diff mean: {scaler.mean_[policy_idx]:.6f}")
    print(f"   Policy_diff std:  {scaler.scale_[policy_idx]:.6f}")
    
    # Guardar artefacto
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pair_safe = pair.replace("/", "_")
    artifact_path = f"{OUTPUT_DIR}/logistic_24_{pair_safe}_{timestamp}.joblib"
    
    artifact = {
        "model": model,
        "feature_names": X.columns.tolist(),
        "horizon": HORIZON,
        "pair": pair,
        "timestamp": timestamp,
        "version": "1.0.0",
        "training_period": {
            "start": X.index[0].strftime("%Y-%m-%d"),
            "end": X.index[-1].strftime("%Y-%m-%d"),
            "n_samples": len(X),
        },
    }
    
    joblib.dump(artifact, artifact_path)
    print(f"   ✅ Modelo guardado: {artifact_path}")
    
    return artifact_path

async def main():
    results = {}
    
    for pair in PAIRS:
        print(f"\n{'='*50}")
        print(f"📥 Cargando datos para {pair}...")
        
        try:
            result = dp.get_historical(pair, period=PERIOD)
            df = result["data"]
            print(f"   Filas: {len(df)}")
            print(f"   Período: {df.index.min()} → {df.index.max()}")
            
            # Obtener policy_diff
            price_dates = pd.DatetimeIndex(df.index)
            policy_diff = await get_policy_diff_for_pair(pair, price_dates)
            
            # Entrenar
            model_path = train_model(pair, df, policy_diff)
            results[pair] = model_path
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results[pair] = None
    
    # Resumen
    print("\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)
    for pair, path in results.items():
        status = "✅" if path else "❌"
        print(f"  {status} {pair}: {path or 'FALLÓ'}")

if __name__ == "__main__":
    asyncio.run(main())
