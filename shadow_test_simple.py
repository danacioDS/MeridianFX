"""
Shadow Test PIT — Logistic_24
Evalúa Logistic_24 sobre las últimas 20 observaciones
usando policy_diff histórico point-in-time.
"""

import asyncio
import json
from datetime import datetime

import numpy as np
import pandas as pd

from backend.layer2.engine import DecisionEngine
from backend.layer2.data.provider import DataProvider
from backend.layer2.features.technical import TechnicalFeatures
from backend.layer2.data.macro.service import MacroService
from backend.layer2.data.macro.differential_provider import (
    MacroDifferentialProvider,
)


print("=== SHADOW TEST PIT — LOGISTIC_24 ===")
print("=" * 70)

engine = DecisionEngine()
dp = DataProvider()

# ------------------------------------------------------------
# 1. Datos históricos
# ------------------------------------------------------------

result = dp.get_historical("EUR/USD", period="1y")
df = result["data"]

print(f"Datos: {len(df)} filas")

df_feat = TechnicalFeatures.generate(df)

technical_cols = TechnicalFeatures.get_feature_names()

print(f"Features técnicas: {len(technical_cols)}")

# ------------------------------------------------------------
# 2. Obtener historia PIT de política monetaria
# ------------------------------------------------------------

price_dates = pd.DatetimeIndex(df_feat.index)

start_date = (
    price_dates.min() - pd.Timedelta(days=10)
).strftime("%Y-%m-%d")

end_date = price_dates.max().strftime("%Y-%m-%d")

print(f"Policy history: {start_date} -> {end_date}")

macro_service = MacroService()

loop = asyncio.new_event_loop()

try:
    asyncio.set_event_loop(loop)

    eur = loop.run_until_complete(
        macro_service.get_historical_policy_rate(
            "EUR",
            start_date,
            end_date,
        )
    )

    usd = loop.run_until_complete(
        macro_service.get_historical_policy_rate(
            "USD",
            start_date,
            end_date,
        )
    )

finally:
    loop.close()


print(f"EUR policy observations: {len(eur)}")
print(f"USD policy observations: {len(usd)}")

# ------------------------------------------------------------
# 3. Construir policy_diff PIT
# ------------------------------------------------------------

policy_diff = MacroDifferentialProvider.calculate_historical(
    base_currency="EUR",
    quote_currency="USD",
    base_series=eur,
    quote_series=usd,
    price_dates=price_dates,
)

print(f"Policy_diff observations: {len(policy_diff)}")

# Alinear exactamente con las fechas de precio
policy_diff = policy_diff.reindex(price_dates)

df_feat["policy_diff"] = policy_diff

# ------------------------------------------------------------
# 4. Construir X canónico
# ------------------------------------------------------------

feature_cols = technical_cols + ["policy_diff"]

X_all = df_feat[feature_cols].copy()

# Eliminar únicamente filas que no pueden evaluarse
X_valid = X_all.dropna()

# Últimas 20 observaciones
X_test = X_valid.tail(20)

print(f"\nObservaciones evaluables: {len(X_valid)}")
print(f"Shadow sample: {len(X_test)}")

# ------------------------------------------------------------
# 5. Cargar Logistic_24
# ------------------------------------------------------------

log_model = engine._get_model_for_pair(
    "EUR/USD",
    "logistic",
)

if log_model is None or log_model.model is None:
    raise RuntimeError(
        "Logistic_24 no está disponible en DecisionEngine"
    )

print("✅ Logistic_24 disponible")

# ------------------------------------------------------------
# 6. Predicciones
# ------------------------------------------------------------

results = []

for date, row in X_test.iterrows():

    X = row.to_frame().T

    pred = log_model.predict(X)

    results.append({
        "date": date.strftime("%Y-%m-%d"),
        "policy_diff": float(row["policy_diff"]),
        "direction": pred["direction"],
        "probability": float(pred["probability"]),
    })

# ------------------------------------------------------------
# 7. Mostrar resultados
# ------------------------------------------------------------

print("\nPredicciones PIT para los últimos 20 días:")
print("-" * 70)

for r in results:
    print(
        f"{r['date']}: "
        f"policy_diff={r['policy_diff']:+.4f} | "
        f"{r['direction']} | "
        f"prob={r['probability']:.6f}"
    )

# ------------------------------------------------------------
# 8. Estadísticas
# ------------------------------------------------------------

probs = np.array(
    [r["probability"] for r in results],
    dtype=float,
)

directions = [
    r["direction"]
    for r in results
]

print("\nEstadísticas:")
print("-" * 70)

print(f"  Prob media: {np.mean(probs):.6f}")
print(f"  Prob std:   {np.std(probs):.6f}")
print(f"  Prob min:   {np.min(probs):.6f}")
print(f"  Prob max:   {np.max(probs):.6f}")

print(
    "  Direcciones:",
    pd.Series(directions).value_counts().to_dict(),
)

# ------------------------------------------------------------
# 9. Guardar resultados
# ------------------------------------------------------------

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

path = f"shadow_test_pit_results_{timestamp}.json"

with open(path, "w") as f:
    json.dump(
        {
            "timestamp": timestamp,
            "model": "Logistic_24",
            "pair": "EUR/USD",
            "feature_count": len(feature_cols),
            "features": feature_cols,
            "results": results,
            "summary": {
                "mean_prob": float(np.mean(probs)),
                "std_prob": float(np.std(probs)),
                "min_prob": float(np.min(probs)),
                "max_prob": float(np.max(probs)),
                "direction_counts": (
                    pd.Series(directions)
                    .value_counts()
                    .to_dict()
                ),
            },
        },
        f,
        indent=2,
    )

print(f"\n✅ Resultados PIT guardados en {path}")
