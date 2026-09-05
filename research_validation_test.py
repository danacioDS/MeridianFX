"""
Investigación formal de MeridianFX
---------------------------------
Protocolo: 60% RESEARCH | 20% VALIDATION | 20% FINAL TEST
Purge = horizon
"""

from backend.layer2.data.provider import DataProvider
from backend.layer2.features.technical import TechnicalFeatures

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator
from sklearn.metrics import (
    roc_auc_score,
    brier_score_loss,
    log_loss,
    balanced_accuracy_score,
    confusion_matrix,
    average_precision_score,
    precision_score,
    recall_score,
    f1_score
)

import numpy as np
import pandas as pd
from datetime import datetime
import json

# Configuración
CANDIDATES = [
    ("GBP/USD", 20),
    ("GBP/USD", 10),
    ("USD/CHF", 30),
    ("USD/CHF", 10),
    ("USD/JPY", 30),
    ("USD/BOB", 20),
    ("EUR/USD", 10),
]

RESEARCH_PCT = 0.60
VALIDATION_PCT = 0.20
FINAL_PCT = 0.20

dp = DataProvider()
results = []

print("=" * 90)
print("MERIDIANFX — FORMAL RESEARCH/VALIDATION/TEST")
print("=" * 90)
print(f"Research:   {RESEARCH_PCT:.0%}")
print(f"Validation: {VALIDATION_PCT:.0%}")
print(f"Final Test: {FINAL_PCT:.0%}")
print("Purge:      horizon")
print("=" * 90)

for pair, h in CANDIDATES:
    print(f"\n{'='*20} {pair} — {h}d {'='*20}")

    # Obtener datos
    result = dp.get_historical(pair, period="2y")
    df = result["data"]
    df_feat = TechnicalFeatures.generate(df)
    feature_cols = TechnicalFeatures.get_feature_names()
    y_all = TechnicalFeatures.create_target(df_feat, forward_days=h)
    X_all = df_feat[feature_cols]

    valid = X_all.notna().all(axis=1) & y_all.notna()
    X = X_all.loc[valid].copy()
    y = y_all.loc[valid].copy()

    n = len(X)
    purge = h

    # División temporal
    research_end = int(n * RESEARCH_PCT)
    validation_end = int(n * (RESEARCH_PCT + VALIDATION_PCT))

    # Research
    X_research = X.iloc[:research_end]
    y_research = y.iloc[:research_end]

    # Validation (con purge)
    val_start = research_end + purge
    val_end = validation_end
    X_val = X.iloc[val_start:val_end]
    y_val = y.iloc[val_start:val_end]

    # Final Test (con purge)
    test_start = validation_end + purge
    X_test = X.iloc[test_start:]
    y_test = y.iloc[test_start:]

    print(f"Total:         {n}")
    print(f"Research:      {len(X_research)}")
    print(f"Validation:    {len(X_val)}")
    print(f"Final Test:    {len(X_test)}")
    print(f"Purge:         {purge}")

    if len(y_val) < 10 or len(y_test) < 10:
        print("⚠️ SKIP — muestra demasiado pequeña")
        continue

    # Entrenar modelo base
    model = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("logistic", LogisticRegression(max_iter=5000, random_state=42))
    ])
    model.fit(X_research, y_research)

    # Evaluación en Validation
    proba_val = model.predict_proba(X_val)[:, 1]
    pred_val = (proba_val >= 0.5).astype(int)

    # Evaluación en Final Test
    proba_test = model.predict_proba(X_test)[:, 1]
    pred_test = (proba_test >= 0.5).astype(int)

    # Calibración (solo en Validation)
    calibrator = CalibratedClassifierCV(
        FrozenEstimator(model),
        method='sigmoid'
    )
    calibrator.fit(X_val, y_val)

    # Probabilidades calibradas en Test
    proba_calibrated = calibrator.predict_proba(X_test)[:, 1]
    pred_calibrated = (proba_calibrated >= 0.5).astype(int)

    # Métricas
    def compute_metrics(y_true, y_pred, y_proba, label):
        return {
            'auc': roc_auc_score(y_true, y_proba),
            'pr_auc': average_precision_score(y_true, y_proba),
            'brier': brier_score_loss(y_true, y_proba),
            'log_loss': log_loss(y_true, y_proba),
            'balanced_accuracy': balanced_accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, zero_division=0),
            'recall': recall_score(y_true, y_pred, zero_division=0),
            'f1': f1_score(y_true, y_pred, zero_division=0),
            'cm': confusion_matrix(y_true, y_pred).tolist(),
            'n_positives': int(y_true.sum()),
            'n_negatives': int((y_true == 0).sum())
        }

    metrics_val = compute_metrics(y_val, pred_val, proba_val, "Validation")
    metrics_test = compute_metrics(y_test, pred_test, proba_test, "Test")
    metrics_calibrated = compute_metrics(y_test, pred_calibrated, proba_calibrated, "Calibrated")

    results.append({
        'pair': pair,
        'horizon': h,
        'validation': metrics_val,
        'test': metrics_test,
        'calibrated': metrics_calibrated,
        'n_research': len(X_research),
        'n_val': len(X_val),
        'n_test': len(X_test)
    })

    print(f"\n--- VALIDATION ---")
    print(f"AUC:         {metrics_val['auc']:.4f}")
    print(f"PR-AUC:      {metrics_val['pr_auc']:.4f}")
    print(f"Brier:       {metrics_val['brier']:.4f}")
    print(f"Bal Acc:     {metrics_val['balanced_accuracy']:.4f}")
    print(f"Precision:   {metrics_val['precision']:.4f}")
    print(f"Recall:      {metrics_val['recall']:.4f}")
    print(f"F1:          {metrics_val['f1']:.4f}")

    print(f"\n--- FINAL TEST (raw) ---")
    print(f"AUC:         {metrics_test['auc']:.4f}")
    print(f"PR-AUC:      {metrics_test['pr_auc']:.4f}")
    print(f"Brier:       {metrics_test['brier']:.4f}")
    print(f"Bal Acc:     {metrics_test['balanced_accuracy']:.4f}")
    print(f"Precision:   {metrics_test['precision']:.4f}")
    print(f"Recall:      {metrics_test['recall']:.4f}")
    print(f"F1:          {metrics_test['f1']:.4f}")

    print(f"\n--- FINAL TEST (calibrated) ---")
    print(f"AUC:         {metrics_calibrated['auc']:.4f}")
    print(f"PR-AUC:      {metrics_calibrated['pr_auc']:.4f}")
    print(f"Brier:       {metrics_calibrated['brier']:.4f}")
    print(f"Bal Acc:     {metrics_calibrated['balanced_accuracy']:.4f}")
    print(f"Precision:   {metrics_calibrated['precision']:.4f}")
    print(f"Recall:      {metrics_calibrated['recall']:.4f}")
    print(f"F1:          {metrics_calibrated['f1']:.4f}")

# Resumen
print("\n" + "=" * 90)
print("RESUMEN FINAL")
print("=" * 90)

summary = []
for r in results:
    summary.append({
        'pair': r['pair'],
        'horizon': r['horizon'],
        'val_auc': r['validation']['auc'],
        'test_auc': r['test']['auc'],
        'test_brier': r['test']['brier'],
        'test_bal_acc': r['test']['balanced_accuracy'],
        'cal_brier': r['calibrated']['brier'],
        'cal_bal_acc': r['calibrated']['balanced_accuracy'],
        'n_test': r['n_test'],
        'test_up': r['test']['n_positives'],
        'test_down': r['test']['n_negatives']
    })

df_summary = pd.DataFrame(summary)
df_summary = df_summary.sort_values('test_auc', ascending=False)

print(df_summary.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

# Guardar resultados
with open('research_validation_results.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

df_summary.to_csv('research_validation_summary.csv', index=False)

print("\n📁 Guardado: research_validation_results.json")
print("📁 Guardado: research_validation_summary.csv")
print("\n" + "=" * 90)
