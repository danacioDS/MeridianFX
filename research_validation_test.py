"""
Investigación formal de MeridianFX
---------------------------------
Protocolo: 60% RESEARCH | 20% VALIDATION | 20% FINAL TEST
Purge = horizon (días) — basado en fechas reales
"""

import numpy as np
import pandas as pd
from datetime import datetime
import json
import warnings

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

warnings.filterwarnings("ignore", category=UserWarning)

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
print("Purge:      horizon (días) — basado en fechas reales")
print("=" * 90)


def compute_metrics(y_true, y_pred, y_proba, label):
    """Calcula métricas con manejo explícito de una sola clase."""
    unique_labels = np.unique(y_true)
    
    metrics = {
        'n_positives': int(np.sum(y_true == 1)),
        'n_negatives': int(np.sum(y_true == 0)),
        'n_samples': int(len(y_true)),
        'unique_labels': unique_labels.tolist(),
    }
    
    if len(unique_labels) < 2:
        metrics.update({
            'auc': np.nan,
            'pr_auc': np.nan,
            'brier': float(brier_score_loss(y_true, y_proba)),
            'log_loss': np.nan,
            'balanced_accuracy': np.nan,
            'precision': np.nan,
            'recall': np.nan,
            'f1': np.nan,
            'cm': confusion_matrix(y_true, y_pred).tolist(),
            'status': 'single_class',
        })
        return metrics
    
    metrics.update({
        'auc': float(roc_auc_score(y_true, y_proba)),
        'pr_auc': float(average_precision_score(y_true, y_proba)),
        'brier': float(brier_score_loss(y_true, y_proba)),
        'log_loss': float(log_loss(y_true, y_proba)),
        'balanced_accuracy': float(balanced_accuracy_score(y_true, y_pred)),
        'precision': float(precision_score(y_true, y_pred, zero_division=0)),
        'recall': float(recall_score(y_true, y_pred, zero_division=0)),
        'f1': float(f1_score(y_true, y_pred, zero_division=0)),
        'cm': confusion_matrix(y_true, y_pred).tolist(),
        'status': 'valid',
    })
    
    return metrics


def get_valid_indices(df_feat, feature_cols, h):
    """Obtiene índices válidos (features completas y target disponible)."""
    y_all = TechnicalFeatures.create_target(df_feat, forward_days=h)
    X_all = df_feat[feature_cols]
    valid = X_all.notna().all(axis=1) & y_all.notna()
    return valid, y_all, X_all


def split_by_date(valid_indices, y_all, X_all, h, research_pct, validation_pct):
    """
    Divide los datos usando fechas reales y purge basado en el horizonte.
    
    Una observación pertenece a Research solamente si su target (h días adelante)
    queda completamente antes del inicio de Validation.
    """
    # Fechas válidas
    valid_dates = X_all.index[valid_indices]
    n_valid = len(valid_dates)
    
    # Límite temporal para Research (basado en porcentaje)
    train_end_idx = int(n_valid * research_pct)
    train_end_date = valid_dates[train_end_idx]
    
    # Purge: el último target de Research no debe cruzar Validation
    # Aproximamos h días hábiles como h * 1.5 días calendario
    purge_days = int(h * 1.5)
    purge_end_date = train_end_date + pd.Timedelta(days=purge_days)
    
    # Validation empieza después del purge
    val_start_date = purge_end_date + pd.Timedelta(days=1)
    
    # Validation: 20% del total
    val_size = int(n_valid * validation_pct)
    val_end_idx = train_end_idx + val_size + 1
    if val_end_idx >= n_valid:
        val_end_idx = n_valid - 1
    val_end_date = valid_dates[val_end_idx]
    
    # Test: después de Validation + purge
    test_start_date = val_end_date + pd.Timedelta(days=purge_days + 1)
    
    # Construir máscaras
    research_mask = (X_all.index >= valid_dates[0]) & (X_all.index <= train_end_date)
    val_mask = (X_all.index >= val_start_date) & (X_all.index <= val_end_date)
    test_mask = (X_all.index >= test_start_date)
    
    # Aplicar máscaras y filtrar por valid_indices
    X_research = X_all.loc[research_mask & valid_indices]
    y_research = y_all.loc[research_mask & valid_indices]
    
    X_val = X_all.loc[val_mask & valid_indices]
    y_val = y_all.loc[val_mask & valid_indices]
    
    X_test = X_all.loc[test_mask & valid_indices]
    y_test = y_all.loc[test_mask & valid_indices]
    
    return X_research, y_research, X_val, y_val, X_test, y_test, {
        'train_end_date': train_end_date,
        'val_start_date': val_start_date,
        'val_end_date': val_end_date,
        'test_start_date': test_start_date,
        'purge_days': purge_days,
    }


def audit_calibration(pair, h, proba_test, proba_calibrated, y_test, model, calibrator, X_val, y_val, proba_val):
    """Auditoría detallada para GBP/USD 10d."""
    if pair != "GBP/USD" or h != 10:
        return
    
    print("\n" + "=" * 90)
    print("🔬 AUDITORÍA DE CALIBRACIÓN — GBP/USD 10d")
    print("=" * 90)
    
    # 1. Clases
    print(f"\n1. CLASES:")
    print(f"   model.classes_:           {model.named_steps['logistic'].classes_}")
    print(f"   calibrator.classes_:      {calibrator.classes_}")
    
    # 2. Probabilidades raw vs calibradas (primeras 10)
    print(f"\n2. PROBABILIDADES (primeras 10):")
    print(f"   {'idx':>4} {'raw':>10} {'cal':>10} {'y_true':>7} {'diff':>10}")
    print(f"   {'---':>4} {'---':>10} {'---':>10} {'------':>7} {'---':>10}")
    for i in range(min(10, len(proba_test))):
        diff = proba_calibrated[i] - proba_test[i]
        print(f"   {i:>4} {proba_test[i]:>10.4f} {proba_calibrated[i]:>10.4f} {int(y_test.iloc[i]):>7} {diff:>10.4f}")
    
    # 3. Estadísticas de probabilidades
    print(f"\n3. ESTADÍSTICAS:")
    print(f"   Raw:")
    print(f"      mean: {np.mean(proba_test):.4f}")
    print(f"      std:  {np.std(proba_test):.4f}")
    print(f"      min:  {np.min(proba_test):.4f}")
    print(f"      max:  {np.max(proba_test):.4f}")
    print(f"   Calibradas:")
    print(f"      mean: {np.mean(proba_calibrated):.4f}")
    print(f"      std:  {np.std(proba_calibrated):.4f}")
    print(f"      min:  {np.min(proba_calibrated):.4f}")
    print(f"      max:  {np.max(proba_calibrated):.4f}")
    
    # 4. Correlación / ranking
    print(f"\n4. RANKING (correlación Spearman entre raw y calibradas):")
    from scipy.stats import spearmanr
    corr, pval = spearmanr(proba_test, proba_calibrated)
    print(f"   Spearman ρ: {corr:.4f} (p={pval:.4f})")
    if corr < 0.5:
        print("   ⚠️ ¡CORRELACIÓN BAJA! La calibración está alterando el ranking.")
    
    # 5. Distribución por clase
    print(f"\n5. DISTRIBUCIÓN POR CLASE:")
    for cls in [0, 1]:
        mask = y_test == cls
        if mask.sum() > 0:
            raw_cls = proba_test[mask]
            cal_cls = proba_calibrated[mask]
            print(f"   Clase {cls} (n={mask.sum()}):")
            print(f"      Raw mean:   {np.mean(raw_cls):.4f}")
            print(f"      Cal mean:   {np.mean(cal_cls):.4f}")
            print(f"      Raw std:    {np.std(raw_cls):.4f}")
            print(f"      Cal std:    {np.std(cal_cls):.4f}")
    
    # 6. AUC por clase
    print(f"\n6. VERIFICACIÓN DE AUC:")
    auc_raw = roc_auc_score(y_test, proba_test)
    auc_cal = roc_auc_score(y_test, proba_calibrated)
    print(f"   AUC raw:  {auc_raw:.4f}")
    print(f"   AUC cal:  {auc_cal:.4f}")
    
    auc_raw_inv = roc_auc_score(1 - y_test, proba_test)
    auc_cal_inv = roc_auc_score(1 - y_test, proba_calibrated)
    print(f"   AUC raw (clase invertida):  {auc_raw_inv:.4f}")
    print(f"   AUC cal (clase invertida):  {auc_cal_inv:.4f}")
    
    # 7. Verificar que la calibración usa la clase correcta
    print(f"\n7. VERIFICACIÓN DE CALIBRADOR:")
    proba_val_cal = calibrator.predict_proba(X_val)[:, 1]
    auc_val_raw = roc_auc_score(y_val, proba_val)
    auc_val_cal = roc_auc_score(y_val, proba_val_cal)
    print(f"   Validation AUC (raw):  {auc_val_raw:.4f}")
    print(f"   Validation AUC (cal):  {auc_val_cal:.4f}")
    
    print("\n" + "=" * 90)


for pair, h in CANDIDATES:
    print(f"\n{'='*20} {pair} — {h}d {'='*20}")
    
    # Obtener datos
    result = dp.get_historical(pair, period="2y")
    df = result["data"]
    df_feat = TechnicalFeatures.generate(df)
    feature_cols = TechnicalFeatures.get_feature_names()
    
    # Obtener índices válidos
    valid_indices, y_all, X_all = get_valid_indices(df_feat, feature_cols, h)
    
    # Dividir usando fechas reales
    X_research, y_research, X_val, y_val, X_test, y_test, split_info = split_by_date(
        valid_indices, y_all, X_all, h, RESEARCH_PCT, VALIDATION_PCT
    )
    
    n = len(X_all[valid_indices])
    purge = h
    
    print(f"Total:         {n}")
    print(f"Research:      {len(X_research)}")
    print(f"Validation:    {len(X_val)}")
    print(f"Final Test:    {len(X_test)}")
    print(f"Purge:         {purge} días")
    print(f"  Research last:  {split_info['train_end_date'].strftime('%Y-%m-%d')}")
    print(f"  Validation start: {split_info['val_start_date'].strftime('%Y-%m-%d')}")
    print(f"  Test start:    {split_info['test_start_date'].strftime('%Y-%m-%d')}")
    
    if len(y_val) < 10 or len(y_test) < 10:
        print("⚠️ SKIP — muestra demasiado pequeña")
        continue
    
    if len(np.unique(y_val)) < 2:
        print("⚠️ SKIP — Validation contiene una sola clase, no se puede calibrar")
        continue
    
    if len(np.unique(y_research)) < 2:
        print("⚠️ SKIP — Research contiene una sola clase, no se puede entrenar")
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
    
    # Calibración
    calibrator = CalibratedClassifierCV(
        FrozenEstimator(model),
        method='sigmoid'
    )
    calibrator.fit(X_val, y_val)
    
    # Evaluación en Final Test
    proba_test = model.predict_proba(X_test)[:, 1]
    pred_test = (proba_test >= 0.5).astype(int)
    
    proba_calibrated = calibrator.predict_proba(X_test)[:, 1]
    pred_calibrated = (proba_calibrated >= 0.5).astype(int)
    
    # Auditoría
    audit_calibration(pair, h, proba_test, proba_calibrated, y_test, model, calibrator, X_val, y_val, proba_val)
    
    # Métricas
    metrics_val = compute_metrics(y_val, pred_val, proba_val, "Validation")
    metrics_test = compute_metrics(y_test, pred_test, proba_test, "Test")
    metrics_calibrated = compute_metrics(y_test, pred_calibrated, proba_calibrated, "Calibrated")
    
    test_status = "VALID" if metrics_test['status'] == 'valid' else "INVALID_TEST_CLASS"
    
    results.append({
        'pair': pair,
        'horizon': h,
        'validation': metrics_val,
        'test': metrics_test,
        'calibrated': metrics_calibrated,
        'n_research': len(X_research),
        'n_val': len(X_val),
        'n_test': len(X_test),
        'test_status': test_status,
        'split_info': {k: str(v) for k, v in split_info.items()},
    })
    
    print(f"\n--- VALIDATION ---")
    if not np.isnan(metrics_val['auc']):
        print(f"AUC:         {metrics_val['auc']:.4f}")
        print(f"PR-AUC:      {metrics_val['pr_auc']:.4f}")
    else:
        print("AUC:         N/A")
        print("PR-AUC:      N/A")
    print(f"Brier:       {metrics_val['brier']:.4f}")
    if not np.isnan(metrics_val['balanced_accuracy']):
        print(f"Bal Acc:     {metrics_val['balanced_accuracy']:.4f}")
        print(f"Precision:   {metrics_val['precision']:.4f}")
        print(f"Recall:      {metrics_val['recall']:.4f}")
        print(f"F1:          {metrics_val['f1']:.4f}")
    else:
        print("Bal Acc:     N/A")
        print("Precision:   N/A")
        print("Recall:      N/A")
        print("F1:          N/A")
    print(f"Positives:   {metrics_val['n_positives']}")
    print(f"Negatives:   {metrics_val['n_negatives']}")
    
    print(f"\n--- FINAL TEST (raw) ---")
    if not np.isnan(metrics_test['auc']):
        print(f"AUC:         {metrics_test['auc']:.4f}")
        print(f"PR-AUC:      {metrics_test['pr_auc']:.4f}")
    else:
        print("AUC:         N/A")
        print("PR-AUC:      N/A")
    print(f"Brier:       {metrics_test['brier']:.4f}")
    if not np.isnan(metrics_test['balanced_accuracy']):
        print(f"Bal Acc:     {metrics_test['balanced_accuracy']:.4f}")
        print(f"Precision:   {metrics_test['precision']:.4f}")
        print(f"Recall:      {metrics_test['recall']:.4f}")
        print(f"F1:          {metrics_test['f1']:.4f}")
    else:
        print("Bal Acc:     N/A")
        print("Precision:   N/A")
        print("Recall:      N/A")
        print("F1:          N/A")
    print(f"Status:      {test_status}")
    print(f"Positives:   {metrics_test['n_positives']}")
    print(f"Negatives:   {metrics_test['n_negatives']}")
    
    print(f"\n--- FINAL TEST (calibrated) ---")
    if not np.isnan(metrics_calibrated['auc']):
        print(f"AUC:         {metrics_calibrated['auc']:.4f}")
        print(f"PR-AUC:      {metrics_calibrated['pr_auc']:.4f}")
    else:
        print("AUC:         N/A")
        print("PR-AUC:      N/A")
    print(f"Brier:       {metrics_calibrated['brier']:.4f}")
    if not np.isnan(metrics_calibrated['balanced_accuracy']):
        print(f"Bal Acc:     {metrics_calibrated['balanced_accuracy']:.4f}")
        print(f"Precision:   {metrics_calibrated['precision']:.4f}")
        print(f"Recall:      {metrics_calibrated['recall']:.4f}")
        print(f"F1:          {metrics_calibrated['f1']:.4f}")
    else:
        print("Bal Acc:     N/A")
        print("Precision:   N/A")
        print("Recall:      N/A")
        print("F1:          N/A")
    print(f"Positives:   {metrics_calibrated['n_positives']}")
    print(f"Negatives:   {metrics_calibrated['n_negatives']}")

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
        'test_status': r['test_status'],
        'cal_brier': r['calibrated']['brier'],
        'cal_bal_acc': r['calibrated']['balanced_accuracy'],
        'n_test': r['n_test'],
        'test_up': r['test']['n_positives'],
        'test_down': r['test']['n_negatives']
    })

df_summary = pd.DataFrame(summary)
df_summary = df_summary.sort_values('test_auc', ascending=False, na_position='last')

print(df_summary.to_string(index=False, float_format=lambda x: f"{x:.4f}" if not np.isnan(x) else "N/A"))

with open('research_validation_results.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

df_summary.to_csv('research_validation_summary.csv', index=False)

print("\n📁 Guardado: research_validation_results.json")
print("📁 Guardado: research_validation_summary.csv")
print("\n" + "=" * 90)
