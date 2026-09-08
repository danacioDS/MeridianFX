"""
MeridianFX — Walk‑Forward con Folds NO Solapados
Prueba robustez de policy_diff en folds independientes

TRAIN = 400
VAL = 100
TEST = 100
STEP = 100 (no solapados)
PURGE = 10
HORIZON = 10
"""

import numpy as np
import pandas as pd
import json
import warnings
import asyncio
import httpx
import copy
from io import StringIO
from datetime import timedelta

from backend.layer2.data.provider import DataProvider
from backend.layer2.features.technical import TechnicalFeatures
from backend.layer2.data.sources.fred import FredDataSource

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
PURGE = HORIZON
TRAIN_OBS = 400
VAL_OBS = 100
TEST_OBS = 100
STEP_OBS = 100  # NO SOLAPADOS

ECB_DFR_KEY = "D.U2.EUR.4F.KR.DFR.LEV"
ECB_URL_DFR = f"https://data-api.ecb.europa.eu/service/data/FM/{ECB_DFR_KEY}"

dp = DataProvider()
fred = FredDataSource()

print("=" * 90)
print("MERIDIANFX — WALK‑FORWARD NO SOLAPADO")
print("=" * 90)
print(f"Pair:              {PAIR}")
print(f"Horizon:           {HORIZON}d")
print(f"Train:             {TRAIN_OBS} obs")
print(f"Validation:        {VAL_OBS} obs")
print(f"Test:              {TEST_OBS} obs")
print(f"Step:              {STEP_OBS} obs (NO SOLAPADO)")
print("=" * 90)


# ============================================================
# FUNCIONES MACRO
# ============================================================

async def fetch_fred_series(series_id, start_date, end_date):
    source = FredDataSource(allow_simulation=False)
    result = await source.fetch_series(series_id, start_date=start_date, end_date=end_date, limit=10000)
    if not result or not result.get("observations"):
        raise RuntimeError(f"FRED no devolvió observaciones para {series_id}.")
    df = pd.DataFrame(result["observations"])
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.normalize().astype("datetime64[ns]")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df[["date", "value"]].dropna().drop_duplicates("date").sort_values("date").reset_index(drop=True)
    if df.empty:
        raise RuntimeError(f"Serie {series_id} vacía después del parsing.")
    print(f"   {series_id}: {df['date'].min().date()} → {df['date'].max().date()} ({len(df)} obs)")
    return df


async def fetch_ecb_series(series_key, start_date, end_date):
    url = f"https://data-api.ecb.europa.eu/service/data/FM/{series_key}"
    params = {"startPeriod": start_date, "endPeriod": end_date, "format": "csvdata"}
    headers = {"Accept": "text/csv"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params, headers=headers)
    if response.status_code != 200:
        raise RuntimeError(f"ECB API error {response.status_code}: {response.text[:500]}")
    text = response.text
    if not text.strip():
        raise RuntimeError("ECB devolvió una respuesta CSV vacía.")
    df = pd.read_csv(StringIO(text))
    if df.empty:
        raise RuntimeError("ECB devolvió 0 observaciones.")
    df.columns = [str(c).strip() for c in df.columns]
    time_col = next((c for c in df.columns if c.upper() in {"TIME_PERIOD", "TIME PERIOD", "DATE"}), None)
    value_col = next((c for c in df.columns if c.upper() in {"OBS_VALUE", "OBS VALUE", "VALUE"}), None)
    if time_col is None or value_col is None:
        raise RuntimeError(f"No se encontraron TIME_PERIOD/OBS_VALUE. Columnas: {list(df.columns)}")
    df["date"] = pd.to_datetime(df[time_col], errors="coerce").dt.normalize().astype("datetime64[ns]")
    df["value"] = pd.to_numeric(df[value_col], errors="coerce")
    df = df[["date", "value"]].dropna().drop_duplicates("date").sort_values("date").reset_index(drop=True)
    if df.empty:
        raise RuntimeError(f"Serie ECB {series_key} vacía después del parsing.")
    print(f"   ECB {series_key}: {df['date'].min().date()} → {df['date'].max().date()} ({len(df)} obs)")
    return df


def get_macro_series_sync(start_date, end_date):
    async def _fetch():
        usd_policy, eur_policy = await asyncio.gather(
            fetch_fred_series("DFF", start_date, end_date),
            fetch_ecb_series(ECB_DFR_KEY, start_date, end_date),
        )
        return usd_policy, eur_policy
    return asyncio.run(_fetch())


def build_point_in_time_policy(price_index):
    price_dates = pd.DatetimeIndex(pd.to_datetime(price_index)).normalize().astype("datetime64[ns]")
    start_date = (price_dates.min() - pd.Timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = price_dates.max().strftime("%Y-%m-%d")
    
    usd_policy, eur_policy = get_macro_series_sync(start_date, end_date)
    
    prices = pd.DataFrame({"date": price_dates}).sort_values("date")
    
    macro = pd.merge_asof(prices, usd_policy.sort_values("date"), on="date", direction="backward")
    macro = macro.rename(columns={"value": "usd_policy"})
    
    macro = pd.merge_asof(macro.sort_values("date"), eur_policy.sort_values("date"), on="date", direction="backward")
    macro = macro.rename(columns={"value": "eur_policy"})
    macro["policy_diff"] = macro["usd_policy"] - macro["eur_policy"]
    
    return macro[["date", "policy_diff"]].set_index("date")


def prepare_dataset(df):
    df_feat = TechnicalFeatures.generate(df)
    technical_cols = TechnicalFeatures.get_feature_names()
    y_all = TechnicalFeatures.create_target(df_feat, forward_days=HORIZON)
    
    policy_df = build_point_in_time_policy(df_feat.index)
    policy_aligned = policy_df.reindex(pd.DatetimeIndex(df_feat.index).normalize())
    policy_aligned.index = df_feat.index
    df_feat["policy_diff"] = policy_aligned["policy_diff"]
    
    # Technical only
    X_tech_all = df_feat[technical_cols]
    valid_tech = X_tech_all.notna().all(axis=1) & y_all.notna()
    X_tech = X_tech_all.loc[valid_tech].copy()
    y_tech = y_all.loc[valid_tech].copy()
    
    # Technical + policy
    cols_policy = technical_cols + ["policy_diff"]
    X_policy_all = df_feat[cols_policy]
    valid_policy = X_policy_all.notna().all(axis=1) & y_all.notna()
    X_policy = X_policy_all.loc[valid_policy].copy()
    y_policy = y_all.loc[valid_policy].copy()
    
    return X_tech, y_tech, X_policy, y_policy


def compute_metrics(y_true, y_pred, y_proba):
    unique_labels = np.unique(y_true)
    metrics = {"n_positives": int(np.sum(y_true == 1)), "n_negatives": int(np.sum(y_true == 0)), "n_samples": int(len(y_true))}
    if len(unique_labels) < 2:
        metrics.update({"auc": np.nan, "pr_auc": np.nan, "brier": float(brier_score_loss(y_true, y_proba)), "balanced_accuracy": np.nan, "precision": np.nan, "recall": np.nan, "f1": np.nan, "cm": confusion_matrix(y_true, y_pred).tolist(), "status": "single_class"})
        return metrics
    metrics.update({"auc": float(roc_auc_score(y_true, y_proba)), "pr_auc": float(average_precision_score(y_true, y_proba)), "brier": float(brier_score_loss(y_true, y_proba)), "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)), "precision": float(precision_score(y_true, y_pred, zero_division=0)), "recall": float(recall_score(y_true, y_pred, zero_division=0)), "f1": float(f1_score(y_true, y_pred, zero_division=0)), "cm": confusion_matrix(y_true, y_pred).tolist(), "status": "valid"})
    return metrics


def build_pipeline(estimator):
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", estimator),
    ])


def run_fold(X, y, train_start, train_end, val_start, val_end, test_start, test_end, model):
    X_train = X.iloc[train_start:train_end]
    y_train = y.iloc[train_start:train_end]
    X_val = X.iloc[val_start:val_end]
    y_val = y.iloc[val_start:val_end]
    X_test = X.iloc[test_start:test_end]
    y_test = y.iloc[test_start:test_end]
    if len(X_train) < 100 or len(X_val) < 20 or len(X_test) < 20:
        return None
    if len(np.unique(y_train)) < 2 or len(np.unique(y_val)) < 2:
        return None
    model.fit(X_train, y_train)
    proba_test = model.predict_proba(X_test)[:, 1]
    pred_test = (proba_test >= 0.5).astype(int)
    calibrator = CalibratedClassifierCV(FrozenEstimator(model), method="sigmoid")
    calibrator.fit(X_val, y_val)
    proba_cal = calibrator.predict_proba(X_test)[:, 1]
    pred_cal = (proba_cal >= 0.5).astype(int)
    raw = compute_metrics(y_test, pred_test, proba_test)
    cal = compute_metrics(y_test, pred_cal, proba_cal)
    return {
        "n_train": len(X_train), "n_val": len(X_val), "n_test": len(X_test),
        "test_start_date": str(X_test.index[0]), "test_end_date": str(X_test.index[-1]),
        "test_auc": raw["auc"], "test_brier": raw["brier"], "test_bal_acc": raw["balanced_accuracy"],
        "cal_auc": cal["auc"], "cal_brier": cal["brier"], "cal_bal_acc": cal["balanced_accuracy"],
        "test_status": raw["status"], "test_up": raw["n_positives"], "test_down": raw["n_negatives"],
    }


def generate_folds(n):
    folds = []
    current_start = 0
    while True:
        train_start = current_start
        train_end = train_start + TRAIN_OBS
        val_start = train_end + PURGE
        val_end = val_start + VAL_OBS
        test_start = val_end + PURGE
        test_end = test_start + TEST_OBS
        if test_end > n:
            break
        folds.append({"fold": len(folds) + 1, "train_start": train_start, "train_end": train_end,
                      "val_start": val_start, "val_end": val_end, "test_start": test_start, "test_end": test_end})
        current_start += STEP_OBS
    return folds


# ============================================================
# PREPARAR DATOS
# ============================================================
print("\n📥 Cargando datos...")
result = dp.get_historical(PAIR, period="4y")
df = result["data"]
print(f"   Filas originales: {len(df)}")
print(f"   Periodo: {df.index.min()} → {df.index.max()}")

print("\n⚙️ Generando features...")
X_tech, y_tech, X_policy, y_policy = prepare_dataset(df)

common_dates = X_tech.index.intersection(X_policy.index)
X_tech = X_tech.loc[common_dates].sort_index()
y_tech = y_tech.loc[common_dates].sort_index()
X_policy = X_policy.loc[common_dates].sort_index()
y_policy = y_policy.loc[common_dates].sort_index()

n = len(common_dates)
print(f"\n🔗 Dataset común: {n} filas")
print(f"   Primera: {common_dates[0]}")
print(f"   Última:  {common_dates[-1]}")

folds = generate_folds(n)
print(f"\n📊 Folds generados: {len(folds)}")

model = build_pipeline(LogisticRegression(max_iter=5000, random_state=42))

# ============================================================
# EJECUTAR
# ============================================================
experiments = {
    "technical_only": (X_tech, y_tech),
    "technical_plus_policy": (X_policy, y_policy),
}

all_results = {}

for exp_name, (X, y) in experiments.items():
    print(f"\n{'='*20} {exp_name} {'='*20}")
    results = []
    for fold_config in folds:
        result = run_fold(X, y,
                          fold_config["train_start"], fold_config["train_end"],
                          fold_config["val_start"], fold_config["val_end"],
                          fold_config["test_start"], fold_config["test_end"],
                          copy.deepcopy(model))
        if result is None:
            continue
        result["fold"] = fold_config["fold"]
        results.append(result)
        print(f"   Fold {result['fold']}: AUC={result['test_auc']:.4f} | Brier={result['test_brier']:.4f}")
    all_results[exp_name] = results

# ============================================================
# RESUMEN
# ============================================================
print("\n" + "=" * 90)
print("RESUMEN — WALK‑FORWARD NO SOLAPADO")
print("=" * 90)

summary_rows = []
for exp_name, results in all_results.items():
    valid = [r for r in results if r["test_status"] == "valid"]
    if not valid:
        continue
    aucs = [r["test_auc"] for r in valid]
    briers = [r["test_brier"] for r in valid]
    summary_rows.append({
        "experiment": exp_name,
        "n_folds": len(valid),
        "auc_mean": np.mean(aucs),
        "auc_std": np.std(aucs),
        "auc_min": np.min(aucs),
        "auc_max": np.max(aucs),
        "brier_mean": np.mean(briers),
        "pct_gt_05": 100 * np.mean([a > 0.50 for a in aucs]),
        "pct_gt_06": 100 * np.mean([a > 0.60 for a in aucs]),
    })

df_summary = pd.DataFrame(summary_rows)
print(df_summary.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

# Efecto incremental
print("\n📈 EFECTO INCREMENTAL (folds no solapados):")
tech = df_summary[df_summary["experiment"] == "technical_only"].iloc[0]
policy = df_summary[df_summary["experiment"] == "technical_plus_policy"].iloc[0]
print(f"   policy_diff ΔAUC:  {policy['auc_mean'] - tech['auc_mean']:+.4f}")
print(f"   policy_diff ΔBrier: {policy['brier_mean'] - tech['brier_mean']:+.4f}")

with open("research_walkforward_nonoverlap_results.json", "w") as f:
    json.dump(all_results, f, indent=2, default=str)

print("\n📁 Guardado: research_walkforward_nonoverlap_results.json")
print("=" * 90)
