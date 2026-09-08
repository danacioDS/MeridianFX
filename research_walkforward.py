"""
MeridianFX — Walk‑Forward Validation (independiente)

Evalúa estabilidad temporal de EUR/USD 10d
usando folds deslizantes con purge basado en observaciones de mercado.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import warnings

from backend.layer2.data.provider import DataProvider
from backend.layer2.features.technical import TechnicalFeatures

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator
from sklearn.metrics import (
    roc_auc_score,
    brier_score_loss,
    balanced_accuracy_score,
    confusion_matrix,
    average_precision_score,
    precision_score,
    recall_score,
    f1_score
)

warnings.filterwarnings("ignore", category=UserWarning)

# ============================================================
# CONFIGURACIÓN
# ============================================================
PAIR = "EUR/USD"
HORIZON = 10
PURGE = HORIZON  # observaciones de mercado

# Tamaños de ventana (en observaciones, no días calendario)
TRAIN_OBS = 400      # ~2 años de datos diarios
VAL_OBS = 100        # ~6 meses
TEST_OBS = 100       # ~6 meses
STEP_OBS = 40        # desplazamiento entre folds (~3 meses)

# Mínimo de folds válidos
MIN_FOLDS = 3

# Gate preliminar
GATE = {
    "auc_mean": 0.75,
    "auc_std": 0.10,
    "auc_min": 0.60,
    "auc_pct_above_05": 0.80,
}

dp = DataProvider()

print("=" * 90)
print("MERIDIANFX — WALK‑FORWARD VALIDATION")
print("=" * 90)
print(f"Pair:              {PAIR}")
print(f"Horizon:           {HORIZON}d")
print(f"Purge:             {PURGE} observaciones de mercado")
print(f"Train size:        {TRAIN_OBS} obs")
print(f"Validation size:   {VAL_OBS} obs")
print(f"Test size:         {TEST_OBS} obs")
print(f"Step size:         {STEP_OBS} obs")
print("=" * 90)


def get_data(pair):
    """Obtiene datos históricos completos."""
    result = dp.get_historical(pair, period="4y")
    return result["data"]


def prepare_features(df, h):
    """Genera features y target sobre toda la serie."""
    df_feat = TechnicalFeatures.generate(df)
    feature_cols = TechnicalFeatures.get_feature_names()
    y_all = TechnicalFeatures.create_target(df_feat, forward_days=h)
    X_all = df_feat[feature_cols]

    valid = X_all.notna().all(axis=1) & y_all.notna()
    X = X_all.loc[valid].copy()
    y = y_all.loc[valid].copy()
    return X, y


def compute_metrics(y_true, y_pred, y_proba, label):
    """Métricas con manejo de una sola clase."""
    unique_labels = np.unique(y_true)

    metrics = {
        'n_positives': int(np.sum(y_true == 1)),
        'n_negatives': int(np.sum(y_true == 0)),
        'n_samples': int(len(y_true)),
    }

    if len(unique_labels) < 2:
        metrics.update({
            'auc': np.nan,
            'pr_auc': np.nan,
            'brier': float(brier_score_loss(y_true, y_proba)),
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
        'balanced_accuracy': float(balanced_accuracy_score(y_true, y_pred)),
        'precision': float(precision_score(y_true, y_pred, zero_division=0)),
        'recall': float(recall_score(y_true, y_pred, zero_division=0)),
        'f1': float(f1_score(y_true, y_pred, zero_division=0)),
        'cm': confusion_matrix(y_true, y_pred).tolist(),
        'status': 'valid',
    })
    return metrics


def run_fold(X, y, train_start, train_end, val_start, val_end, test_start, test_end):
    """Ejecuta un fold con entrenamiento, calibración y evaluación."""
    # Extraer datos
    X_train = X.iloc[train_start:train_end]
    y_train = y.iloc[train_start:train_end]
    X_val = X.iloc[val_start:val_end]
    y_val = y.iloc[val_start:val_end]
    X_test = X.iloc[test_start:test_end]
    y_test = y.iloc[test_start:test_end]

    # Verificar suficientes datos
    if len(X_train) < 100 or len(X_val) < 20 or len(X_test) < 20:
        return None

    if len(np.unique(y_train)) < 2 or len(np.unique(y_val)) < 2:
        return None

    # Entrenar modelo
    model = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("logistic", LogisticRegression(max_iter=5000, random_state=42))
    ])
    model.fit(X_train, y_train)

    # Evaluar en Validation (raw)
    proba_val = model.predict_proba(X_val)[:, 1]
    pred_val = (proba_val >= 0.5).astype(int)

    # Calibrar en Validation
    calibrator = CalibratedClassifierCV(
        FrozenEstimator(model),
        method='sigmoid'
    )
    calibrator.fit(X_val, y_val)

    # Test (raw)
    proba_test = model.predict_proba(X_test)[:, 1]
    pred_test = (proba_test >= 0.5).astype(int)

    # Test (calibrado)
    proba_cal = calibrator.predict_proba(X_test)[:, 1]
    pred_cal = (proba_cal >= 0.5).astype(int)

    # Métricas
    metrics_test = compute_metrics(y_test, pred_test, proba_test, "Test")
    metrics_cal = compute_metrics(y_test, pred_cal, proba_cal, "Calibrated")

    # Verificar Spearman para detectar inversión de ranking
    from scipy.stats import spearmanr
    corr, _ = spearmanr(proba_test, proba_cal)
    ranking_inverted = corr < -0.5

    return {
        'fold': None,  # se asigna después
        'train_start': train_start,
        'train_end': train_end,
        'val_start': val_start,
        'val_end': val_end,
        'test_start': test_start,
        'test_end': test_end,
        'n_train': len(X_train),
        'n_val': len(X_val),
        'n_test': len(X_test),
        'test_auc': metrics_test['auc'],
        'test_brier': metrics_test['brier'],
        'test_bal_acc': metrics_test['balanced_accuracy'],
        'cal_auc': metrics_cal['auc'],
        'cal_brier': metrics_cal['brier'],
        'cal_bal_acc': metrics_cal['balanced_accuracy'],
        'test_status': metrics_test['status'],
        'test_up': metrics_test['n_positives'],
        'test_down': metrics_test['n_negatives'],
        'cal_up': metrics_cal['n_positives'],
        'cal_down': metrics_cal['n_negatives'],
        'ranking_inverted': ranking_inverted,
        'spearman_corr': corr,
    }


# ============================================================
# GENERAR FOLDS
# ============================================================
print("\n📥 Cargando datos...")
df = get_data(PAIR)
print(f"   Filas originales: {len(df)}")

print("\n⚙️ Generando features y target...")
X, y = prepare_features(df, HORIZON)
n = len(X)
print(f"   Filas válidas: {n}")
print(f"   Primera fecha: {X.index[0]}")
print(f"   Última fecha:  {X.index[-1]}")

# Calcular folds
folds = []
current_start = 0

while True:
    train_start = current_start
    train_end = train_start + TRAIN_OBS

    val_start = train_end + PURGE
    val_end = val_start + VAL_OBS

    test_start = val_end + PURGE
    test_end = test_start + TEST_OBS

    # Verificar que el test cabe
    if test_end > n:
        break

    folds.append({
        'train_start': train_start,
        'train_end': train_end,
        'val_start': val_start,
        'val_end': val_end,
        'test_start': test_start,
        'test_end': test_end,
        'fold': len(folds) + 1,
    })

    current_start += STEP_OBS

print(f"\n📊 Folds generados: {len(folds)}")

# ============================================================
# EJECUTAR FOLDS
# ============================================================
results = []

for fold_config in folds:
    fold_num = fold_config['fold']
    print(f"\n{'='*20} FOLD {fold_num} {'='*20}")

    result = run_fold(
        X, y,
        fold_config['train_start'],
        fold_config['train_end'],
        fold_config['val_start'],
        fold_config['val_end'],
        fold_config['test_start'],
        fold_config['test_end']
    )

    if result is None:
        print("   ⚠️ SKIP — datos insuficientes o clase única")
        continue

    result['fold'] = fold_num
    results.append(result)

    print(f"   Train:  {result['train_start']} → {result['train_end']} ({result['n_train']} obs)")
    print(f"   Purge:  {PURGE} obs")
    print(f"   Val:    {result['val_start']} → {result['val_end']} ({result['n_val']} obs)")
    print(f"   Purge:  {PURGE} obs")
    print(f"   Test:   {result['test_start']} → {result['test_end']} ({result['n_test']} obs)")
    print(f"   Fechas:")
    print(f"      Train: {X.index[result['train_start']]} → {X.index[result['train_end']-1]}")
    print(f"      Val:   {X.index[result['val_start']]} → {X.index[result['val_end']-1]}")
    print(f"      Test:  {X.index[result['test_start']]} → {X.index[result['test_end']-1]}")

    if result['test_status'] != 'valid':
        print(f"   ⚠️ Test inválido: {result['test_status']}")
        continue

    print(f"\n   TEST (raw):")
    print(f"      AUC:         {result['test_auc']:.4f}")
    print(f"      Brier:       {result['test_brier']:.4f}")
    print(f"      Bal Acc:     {result['test_bal_acc']:.4f}")
    print(f"      Positives:   {result['test_up']}")
    print(f"      Negatives:   {result['test_down']}")

    print(f"\n   TEST (calibrado):")
    print(f"      AUC:         {result['cal_auc']:.4f}")
    print(f"      Brier:       {result['cal_brier']:.4f}")
    print(f"      Bal Acc:     {result['cal_bal_acc']:.4f}")

    if result['ranking_inverted']:
        print(f"   🔴 RANKING INVERTIDO (Spearman ρ = {result['spearman_corr']:.4f})")
    else:
        print(f"   🟢 Ranking estable (Spearman ρ = {result['spearman_corr']:.4f})")

# ============================================================
# RESUMEN
# ============================================================
print("\n" + "=" * 90)
print("RESUMEN WALK‑FORWARD")
print("=" * 90)

valid_folds = [r for r in results if r['test_status'] == 'valid']
print(f"\nFolds válidos: {len(valid_folds)} / {len(results)}")

if len(valid_folds) < MIN_FOLDS:
    print(f"⚠️ Folds insuficientes ({len(valid_folds)} < {MIN_FOLDS})")
    print("   No se puede aplicar el gate.")
    print("\n" + "=" * 90)
    exit(0)

# Estadísticas
aucs = [r['test_auc'] for r in valid_folds]
aucs_cal = [r['cal_auc'] for r in valid_folds]
briers = [r['test_brier'] for r in valid_folds]
briers_cal = [r['cal_brier'] for r in valid_folds]

print("\n📊 ESTADÍSTICAS (raw):")
print(f"   AUC media:      {np.mean(aucs):.4f}")
print(f"   AUC std:        {np.std(aucs):.4f}")
print(f"   AUC min:        {np.min(aucs):.4f}")
print(f"   AUC max:        {np.max(aucs):.4f}")
print(f"   % folds AUC>0.50: {100 * np.mean([a > 0.50 for a in aucs]):.1f}%")
print(f"   Brier media:    {np.mean(briers):.4f}")

print("\n📊 ESTADÍSTICAS (calibrado):")
print(f"   AUC media:      {np.mean(aucs_cal):.4f}")
print(f"   AUC std:        {np.std(aucs_cal):.4f}")
print(f"   AUC min:        {np.min(aucs_cal):.4f}")
print(f"   AUC max:        {np.max(aucs_cal):.4f}")
print(f"   Brier media:    {np.mean(briers_cal):.4f}")

# Calibración: ¿mejora Brier?
brier_improvement = np.mean([r['test_brier'] - r['cal_brier'] for r in valid_folds])
pct_brier_improved = 100 * np.mean([r['test_brier'] > r['cal_brier'] for r in valid_folds])

print(f"\n📊 CALIBRACIÓN:")
print(f"   Mejora Brier media: {brier_improvement:.4f}")
print(f"   % folds con mejora: {pct_brier_improved:.1f}%")

# Ranking invertido
inverted_folds = [r for r in valid_folds if r['ranking_inverted']]
print(f"\n📊 RANKING:")
print(f"   Folds con ranking invertido: {len(inverted_folds)} / {len(valid_folds)}")

# ============================================================
# GATE
# ============================================================
print("\n" + "=" * 90)
print("GATE PRELIMINAR")
print("=" * 90)

gate_passed = True
gate_results = []

# 1. AUC medio
auc_mean = np.mean(aucs)
gate_auc_mean = auc_mean >= GATE["auc_mean"]
gate_results.append(("AUC medio ≥ 0.75", auc_mean, GATE["auc_mean"], gate_auc_mean))

# 2. AUC std
auc_std = np.std(aucs)
gate_auc_std = auc_std < GATE["auc_std"]
gate_results.append(("AUC std < 0.10", auc_std, GATE["auc_std"], gate_auc_std))

# 3. AUC min
auc_min = np.min(aucs)
gate_auc_min = auc_min > GATE["auc_min"]
gate_results.append(("AUC min > 0.60", auc_min, GATE["auc_min"], gate_auc_min))

# 4. % folds AUC > 0.50
pct_above_05 = 100 * np.mean([a > 0.50 for a in aucs])
gate_auc_pct = pct_above_05 >= 80
gate_results.append(("% folds AUC>0.50 ≥ 80%", pct_above_05, "80%", gate_auc_pct))

# 5. Calibración estable (Brier mejora en mayoría)
gate_calibration = pct_brier_improved >= 60
gate_results.append(("Brier mejora en ≥60% folds", pct_brier_improved, "60%", gate_calibration))

# 6. Sin ranking invertido
gate_ranking = len(inverted_folds) == 0
gate_results.append(("0 folds con ranking invertido", len(inverted_folds), "0", gate_ranking))

print("\nResultados:")
for name, value, threshold, passed in gate_results:
    status = "✅" if passed else "❌"
    if isinstance(value, float):
        print(f"   {status} {name}: {value:.4f} (umbral: {threshold})")
    else:
        print(f"   {status} {name}: {value} (umbral: {threshold})")

gate_passed = all(r[3] for r in gate_results)

print("\n" + "=" * 90)
if gate_passed:
    print("✅ GATE SUPERADO — EUR/USD 10d es candidato a producción")
else:
    print("❌ GATE NO SUPERADO — EUR/USD 10d requiere revisión")
print("=" * 90)

# Guardar resultados
summary = {
    'pair': PAIR,
    'horizon': HORIZON,
    'n_folds': len(valid_folds),
    'auc_mean': float(np.mean(aucs)),
    'auc_std': float(np.std(aucs)),
    'auc_min': float(np.min(aucs)),
    'auc_max': float(np.max(aucs)),
    'pct_above_05': float(pct_above_05),
    'brier_mean': float(np.mean(briers)),
    'cal_auc_mean': float(np.mean(aucs_cal)),
    'cal_brier_mean': float(np.mean(briers_cal)),
    'brier_improvement': float(brier_improvement),
    'pct_brier_improved': float(pct_brier_improved),
    'inverted_folds': len(inverted_folds),
    'gate_passed': gate_passed,
    'folds': valid_folds,
}

with open('research_walkforward_results.json', 'w') as f:
    json.dump(summary, f, indent=2, default=str)

print("\n📁 Guardado: research_walkforward_results.json")
