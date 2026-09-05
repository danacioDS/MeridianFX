from backend.layer2.data.provider import DataProvider
from backend.layer2.features.technical import TechnicalFeatures

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    roc_auc_score,
    brier_score_loss,
    balanced_accuracy_score,
    confusion_matrix,
    average_precision_score
)

import numpy as np
import pandas as pd

CANDIDATES = [
    ("USD/BOB", 20),
    ("GBP/USD", 10),
    ("GBP/USD", 20),
    ("USD/CHF", 10),
    ("USD/CHF", 30),
    ("USD/JPY", 30),
    ("EUR/USD", 10),
    ("USD/BRL", 10),
]

HOLDOUT = 0.20
PURGE = 30

dp = DataProvider()

results = []

print("=" * 90)
print("MERIDIANFX — FINAL UNTOUCHED HOLDOUT")
print("=" * 90)
print(f"Holdout: {HOLDOUT:.0%}")
print(f"Purged gap: {PURGE}")
print("=" * 90)

for pair, h in CANDIDATES:

    print(f"\n{'='*20} {pair} — {h}d {'='*20}")

    result = dp.get_historical(pair, period="2y")
    df = result["data"]

    df_feat = TechnicalFeatures.generate(df)
    feature_cols = TechnicalFeatures.get_feature_names()

    y_all = TechnicalFeatures.create_target(
        df_feat,
        forward_days=h
    )

    X_all = df_feat[feature_cols]

    valid = X_all.notna().all(axis=1) & y_all.notna()

    X = X_all.loc[valid].copy()
    y = y_all.loc[valid].copy()

    n = len(X)

    # Holdout temporal final
    test_size = int(n * HOLDOUT)

    train_end = n - test_size - PURGE
    test_start = train_end + PURGE

    X_train = X.iloc[:train_end]
    y_train = y.iloc[:train_end]

    X_test = X.iloc[test_start:]
    y_test = y.iloc[test_start:]

    print(f"Total válido : {n}")
    print(f"Train        : {len(X_train)}")
    print(f"Gap          : {PURGE}")
    print(f"Holdout      : {len(X_test)}")
    print(f"Train classes: {y_train.value_counts().to_dict()}")
    print(f"Test classes : {y_test.value_counts().to_dict()}")

    if y_train.nunique() < 2 or y_test.nunique() < 2:
        print("⚠️ SKIP — una sola clase")
        continue

    model = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("logistic", LogisticRegression(
            max_iter=5000,
            random_state=42
        ))
    ])

    model.fit(X_train, y_train)

    prob = model.predict_proba(X_test)[:, 1]
    pred = (prob >= 0.5).astype(int)

    auc = roc_auc_score(y_test, prob)
    pr_auc = average_precision_score(y_test, prob)
    brier = brier_score_loss(y_test, prob)
    bal_acc = balanced_accuracy_score(y_test, pred)
    cm = confusion_matrix(y_test, pred)

    print(f"\nAUC:              {auc:.4f}")
    print(f"PR-AUC:           {pr_auc:.4f}")
    print(f"Brier:            {brier:.4f}")
    print(f"Balanced Accuracy: {bal_acc:.4f}")
    print("Confusion Matrix:")
    print(cm)

    results.append({
        "pair": pair,
        "horizon": h,
        "n_train": len(X_train),
        "n_test": len(X_test),
        "test_up": int(y_test.sum()),
        "test_down": int((y_test == 0).sum()),
        "auc": auc,
        "pr_auc": pr_auc,
        "brier": brier,
        "balanced_accuracy": bal_acc,
    })

print("\n")
print("=" * 90)
print("FINAL HOLDOUT RESULTS")
print("=" * 90)

if results:
    out = pd.DataFrame(results)
    out = out.sort_values("auc", ascending=False)

    print(
        out.to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}"
        )
    )

    out.to_csv("final_holdout_results.csv", index=False)

    print("\n📁 Guardado: final_holdout_results.csv")

else:
    print("No hay resultados válidos.")
