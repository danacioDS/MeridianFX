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

from backend.layer3.artifacts.schema import (
    FeatureProvenance,
    ValidationMetrics,
    build_artifact,
    validate_artifact,
)
from backend.layer3.artifacts.validate import run_walk_forward

print("=" * 70)
print("MERIDIANFX — ENTRENAMIENTO MULTI-PARES")
print("=" * 70)

# Configuración
PAIRS = [
    "EUR/USD", "GBP/USD", "USD/JPY",
    "USD/CHF", "USD/MXN", "USD/BRL",
]
HORIZON = 10
OUTPUT_DIR = "models/canonical"
PERIOD = "4y"

dp = DataProvider()
macro_service = MacroService()

async def get_policy_diff_for_pair(pair, price_dates):
    """
    Obtiene policy_diff PIT usando el provider registrado para cada moneda.

    Ya no usa proxies ni constantes: si un provider no tiene histórico,
    devuelve NaN y el SimpleImputer(median) lo maneja. El artefacto
    registrará feature_provenance.available=False en ese caso.
    """
    from backend.layer2.data.macro import CountryMacroRegistry

    base, quote = pair.split('/')

    start_date = (price_dates.min() - pd.Timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = price_dates.max().strftime("%Y-%m-%d")

    base_prov = CountryMacroRegistry.get(base)
    quote_prov = CountryMacroRegistry.get(quote)

    if base_prov is None or quote_prov is None:
        missing = base if base_prov is None else quote
        print(f"   ⚠️ {pair}: sin provider para {missing}; policy_diff=NaN")
        return pd.Series(np.nan, index=price_dates, name="policy_diff")

    if not hasattr(base_prov, "get_historical") or not hasattr(quote_prov, "get_historical"):
        print(f"   ⚠️ {pair}: provider sin get_historical; policy_diff=NaN")
        return pd.Series(np.nan, index=price_dates, name="policy_diff")

    base_df = await base_prov.get_historical(start_date, end_date)
    quote_df = await quote_prov.get_historical(start_date, end_date)

    if base_df.empty or quote_df.empty:
        print(
            f"   ⚠️ {pair}: histórico vacío "
            f"(base={len(base_df)}, quote={len(quote_df)}); policy_diff=NaN"
        )
        return pd.Series(np.nan, index=price_dates, name="policy_diff")

    policy_diff = MacroDifferentialProvider.calculate_historical(
        base_currency=base,
        quote_currency=quote,
        base_series=base_df,
        quote_series=quote_df,
        price_dates=price_dates,
    )
    return policy_diff

async def train_model(pair, df, policy_diff):
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

    # Feature provenance: 23 técnicas + policy_diff del provider real
    from backend.layer2.data.macro import CountryMacroRegistry
    from backend.layer2.data.macro.differential_provider import MacroDifferentialProvider

    prov = CountryMacroRegistry.get(pair.split("/")[1])

    # Consultar el provider directamente para saber cuántas observaciones
    # son reales. calculate_historical hace forward-fill, así que notna()
    # sobre policy_diff no sirve para esto.
    real_obs = 0
    last_real = None
    if prov is not None and hasattr(prov, "get_historical"):
        try:
            start_dt = (X.index.min() - pd.Timedelta(days=30)).strftime("%Y-%m-%d")
            end_dt = X.index.max().strftime("%Y-%m-%d")
            real_df = await prov.get_historical(start_dt, end_dt)
            real_obs = len(real_df)
            if not real_df.empty:
                last_real = real_df["date"].max()
        except Exception as e:
            print(f"   ⚠️ {pair}: error consultando {type(prov).__name__}: {e}")

    expected_obs = int(len(policy_diff)) if policy_diff is not None else 0
    policy_available = real_obs > 0

    if last_real is not None and last_real < pd.Timestamp(X.index.max()):
        forward_filled = expected_obs - real_obs
        policy_notes = (
            f"{real_obs} obs reales del provider hasta {last_real.date()}; "
            f"{forward_filled} fechas forward-filled"
        )
    elif real_obs > 0:
        if real_obs >= expected_obs:
            policy_notes = f"{real_obs} obs reales cubren las {expected_obs} fechas"
        else:
            policy_notes = f"{real_obs}/{expected_obs} obs reales"
    else:
        policy_notes = "sin observaciones reales del provider"

    feature_prov = [
        FeatureProvenance(name=c, source="TechnicalFeatures", semantic_label=c)
        for c in technical_cols
    ]
    feature_prov.append(FeatureProvenance(
        name="policy_diff",
        source=type(prov).__name__ if prov else "unknown",
        series=getattr(type(prov), "SERIES_ID", None) if prov else None,
        semantic_label="policy rate differential",
        transform=f"clip((base - quote) / {MacroDifferentialProvider.POLICY_SCALE}, -1, 1)",
        available=policy_available,
        notes=policy_notes,
    ))

    # Provisional: validation se rellena después del walk-forward
    artifact = build_artifact(
        pair=pair,
        model=model,
        X=X,
        y=y,
        horizon=HORIZON,
        feature_provenance=feature_prov,
        validation=ValidationMetrics(
            protocol="pending_walk_forward",
            validated=False,
            promotion_status="PENDING",
            notes="to be replaced by run_walk_forward after training",
        ),
    )

    joblib.dump(artifact, artifact_path)
    print(f"   ✅ Modelo guardado: {artifact_path} (provisional)")

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

            # Entrenar (provisional, validation=PENDING)
            model_path = await train_model(pair, df, policy_diff)

            # Walk-forward + promotion gate
            if model_path and os.path.exists(model_path):
                print(f"   🔬 Corriendo walk-forward para {pair}…")
                validation = await run_walk_forward(pair)
                print(f"   Validation: {validation.promotion_status} "
                      f"(val_auc={validation.auc}, cal_brier={validation.cal_brier})")
                for r in validation.reasons:
                    print(f"     ✗ {r}")
                for w in validation.warnings:
                    print(f"     ⚠ {w}")

                # Actualizar el artefacto con las métricas reales
                import joblib
                from dataclasses import asdict
                artifact = joblib.load(model_path)
                artifact["validation"] = asdict(validation)
                artifact["promotion_status"] = validation.promotion_status

                errors = validate_artifact(artifact)
                if errors:
                    print(f"   ⚠ artefacto inválido: {errors}")
                else:
                    joblib.dump(artifact, model_path)
                    print(f"   ✅ Artefacto actualizado: {validation.promotion_status}")

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
