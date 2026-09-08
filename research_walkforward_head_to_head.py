"""
MeridianFX — Head-to-Head Comparison
Mismo snapshot PIT para todos los modelos

Compara:
1. XGBoost + 23 features (producción actual)
2. XGBoost + 24 features (producción + policy_diff)
3. Logistic (spec producción) + 23 features
4. Logistic (spec producción) + 24 features
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

try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except ImportError:
    HAS_XGB = False
    print("⚠️ XGBoost no instalado. Se omitirá.")

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
STEP_OBS = 40

ECB_DFR_KEY = "D.U2.EUR.4F.KR.DFR.LEV"
ECB_URL_DFR = f"https://data-api.ecb.europa.eu/service/data/FM/{ECB_DFR_KEY}"

dp = DataProvider()
fred = FredDataSource()

print("=" * 90)
print("MERIDIANFX — HEAD-TO-HEAD COMPARISON")
print("=" * 90)
print(f"Pair:              {PAIR}")
print(f"Horizon:           {HORIZON}d")
print(f"Train:             {TRAIN_OBS} obs")
print(f"Validation:        {VAL_OBS} obs")
print(f"Test:              {TEST_OBS} obs")
print(f"Step:              {STEP_OBS} obs")
print("=" * 90)


# ============================================================
# FUNCIONES MACRO (PIT canónico)
# ============================================================

async def fetch_usd_policy_history(start_date, end_date):
    source = FredDataSource(allow_simulation=False)
    result = await source.fetch_series("DFF", start_date=start_date, end_date=end_date, limit=10000)
    if not result or not result.get("observations"):
        raise RuntimeError("FRED no devolvió observaciones históricas para DFF.")
    df = pd.DataFrame(result["observations"])
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.normalize().astype("datetime64[ns]")
    df["policy_rate"] = pd.to_numeric(df["value"], errors="coerce")
    df = df[["date", "policy_rate"]].dropna().drop_duplicates("date").sort_values("date").reset_index(drop=True)
    if df.empty:
        raise RuntimeError("Serie FRED DFF vacía después del parsing.")
    print(f"   USD policy history: {df['date'].min().date()} → {df['date'].max().date()} ({len(df)} obs)")
    return df


async def fetch_eur_policy_history(start_date, end_date):
    url = f"https://data-api.ecb.europa.eu/service/data/FM/{ECB_DFR_KEY}"
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
    df["policy_rate"] = pd.to_numeric(df[value_col], errors="coerce")
    df = df[["date", "policy_rate"]].dropna().drop_duplicates("date").sort_values("date").reset_index(drop=True)
    if df.empty:
        raise RuntimeError("Serie ECB vacía después del parsing.")
    print(f"   EUR policy history: {df['date'].min().date()} → {df['date'].max().date()} ({len(df)} obs)")
    return df


def get_policy_history_sync(start_date, end_date):
    async def _fetch():
        usd, eur = await asyncio.gather(
            fetch_usd_policy_history(start_date, end_date),
            fetch_eur_policy_history(start_date, end_date),
        )
        return usd, eur
    return asyncio.run(_fetch())


def build_point_in_time_policy(price_index):
    if len(price_index) == 0:
        raise ValueError("price_index vacío.")
    
    price_dates = pd.DatetimeIndex(pd.to_datetime(price_index)).normalize().astype("datetime64[ns]")
    start_date = (price_dates.min() - pd.Timedelta(days=10)).strftime("%Y-%m-%d")
    end_date = price_dates.max().strftime("%Y-%m-%d")
    
    usd, eur = get_policy_history_sync(start_date, end_date)
    
    from backend.layer2.data.macro.differential_provider import MacroDifferentialProvider
    
    policy_diff = MacroDifferentialProvider.calculate_historical(
        base_currency="USD",
        quote_currency="EUR",
        base_series=usd,
        quote_series=eur,
        price_dates=price_dates,
    )
    
    return policy_diff.to_frame("policy_diff")


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
    
    # Technical + Macro
    macro_cols = ["policy_diff"]
    X_macro_all = df_feat[technical_cols + macro_cols]
    valid_macro = X_macro_all.notna().all(axis=1) & y_all.notna()
    X_macro = X_macro_all.loc[valid_macro].copy()
    y_macro = y_all.loc[valid_macro].copy()
    
    return X_tech, y_tech, X_macro, y_macro, technical_cols, macro_cols


def compute_metrics(y_true, y_pred, y_proba):
    unique_labels = np.unique(y_true)
    metrics = {
        "n_positives": int(np.sum(y_true == 1)),
        "n_negatives": int(np.sum(y_true == 0)),
        "n_samples": int(len(y_true)),
    }
    if len(unique_labels) < 2:
        metrics.update({"auc": np.nan, "pr_auc": np.nan, "brier": float(brier_score_loss(y_true, y_proba)), "balanced_accuracy": np.nan, "precision": np.nan, "recall": np.nan, "f1": np.nan, "cm": confusion_matrix(y_true, y_pred).tolist(), "status": "single_class"})
        return metrics
    metrics.update({"auc": float(roc_auc_score(y_true, y_proba)), "pr_auc": float(average_precision_score(y_true, y_proba)), "brier": float(brier_score_loss(y_true, y_proba)), "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)), "precision": float(precision_score(y_true, y_pred, zero_division=0)), "recall": float(recall_score(y_true, y_pred, zero_division=0)), "f1": float(f1_score(y_true, y_pred, zero_division=0)), "cm": confusion_matrix(y_true, y_pred).tolist(), "status": "valid"})
    return metrics


def build_logistic_pipeline():
    """LogisticRegression con configuración de producción (class_weight='balanced')."""
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(
            C=1.0,
            max_iter=1000,
            random_state=42,
            class_weight="balanced",
        )),
    ])


def build_xgboost_pipeline():
    """XGBoost con configuración de producción."""
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", XGBClassifier(
            n_estimators=100,
            learning_rate=0.05,
            max_depth=5,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric="logloss",
            enable_categorical=False,
        )),
    ])


def run_fold(X, y, train_start, train_end, val_start, val_end, test_start, test_end, model_builder):
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
    
    model = model_builder()
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
X_tech, y_tech, X_macro, y_macro, tech_cols, macro_cols = prepare_dataset(df)

common_dates = X_tech.index.intersection(X_macro.index)
X_tech = X_tech.loc[common_dates].sort_index()
y_tech = y_tech.loc[common_dates].sort_index()
X_macro = X_macro.loc[common_dates].sort_index()
y_macro = y_macro.loc[common_dates].sort_index()

n = len(common_dates)
print(f"\n🔗 Dataset común: {n} filas")
print(f"   Primera: {common_dates[0]}")
print(f"   Última:  {common_dates[-1]}")

folds = generate_folds(n)
print(f"\n📊 Folds generados: {len(folds)}")

# ============================================================
# EXPERIMENTOS
# ============================================================
experiments = [
    ("XGBoost_23", X_tech, y_tech, build_xgboost_pipeline),
    ("XGBoost_24", X_macro, y_macro, build_xgboost_pipeline),
    ("Logistic_23", X_tech, y_tech, build_logistic_pipeline),
    ("Logistic_24", X_macro, y_macro, build_logistic_pipeline),
]

all_results = {}

for name, X, y, builder in experiments:
    print(f"\n{'='*20} {name} {'='*20}")
    results = []
    for fold_config in folds:
        result = run_fold(X, y,
                          fold_config["train_start"], fold_config["train_end"],
                          fold_config["val_start"], fold_config["val_end"],
                          fold_config["test_start"], fold_config["test_end"],
                          builder)
        if result is None:
            continue
        result["fold"] = fold_config["fold"]
        results.append(result)
        auc_str = f"{result['test_auc']:.4f}" if not np.isnan(result['test_auc']) else "N/A"
        print(f"   Fold {result['fold']}: AUC={auc_str} | Brier={result['test_brier']:.4f}")
    all_results[name] = results

# ============================================================
# RESUMEN
# ============================================================
print("\n" + "=" * 90)
print("RESUMEN HEAD-TO-HEAD")
print("=" * 90)

summary_rows = []
for name, results in all_results.items():
    valid = [r for r in results if r["test_status"] == "valid"]
    if not valid:
        continue
    aucs = [r["test_auc"] for r in valid]
    briers = [r["test_brier"] for r in valid]
    summary_rows.append({
        "model": name,
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
df_summary = df_summary.sort_values("auc_mean", ascending=False)
print(df_summary.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

print("\n📈 COMPARATIVA CLAVE:")
logistic_23 = df_summary[df_summary["model"] == "Logistic_23"].iloc[0]
logistic_24 = df_summary[df_summary["model"] == "Logistic_24"].iloc[0]
xgboost_23 = df_summary[df_summary["model"] == "XGBoost_23"].iloc[0]
xgboost_24 = df_summary[df_summary["model"] == "XGBoost_24"].iloc[0]

print(f"   Logistic_23 AUC:          {logistic_23['auc_mean']:.4f}")
print(f"   Logistic_24 AUC:          {logistic_24['auc_mean']:.4f}  (Δ +{logistic_24['auc_mean'] - logistic_23['auc_mean']:.4f})")
print(f"   XGBoost_23 AUC:           {xgboost_23['auc_mean']:.4f}")
print(f"   XGBoost_24 AUC:           {xgboost_24['auc_mean']:.4f}  (Δ {xgboost_24['auc_mean'] - xgboost_23['auc_mean']:+.4f})")
print()
print(f"   Logistic_24 vs XGBoost_23:  Δ {logistic_24['auc_mean'] - xgboost_23['auc_mean']:+.4f}")

with open("research_walkforward_head_to_head_results.json", "w") as f:
    json.dump(all_results, f, indent=2, default=str)

print("\n📁 Guardado: research_walkforward_head_to_head_results.json")
print("=" * 90)
