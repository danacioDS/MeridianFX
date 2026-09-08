"""
MeridianFX — Walk‑Forward con diferentes modelos
Compara LogisticRegression, RandomForest, XGBoost
con y sin policy_diff
"""

import numpy as np
import pandas as pd
import json
import copy
import warnings
import asyncio
import httpx
from io import StringIO

from backend.layer2.data.provider import DataProvider
from backend.layer2.features.technical import TechnicalFeatures
from backend.layer2.data.sources.fred import FredDataSource

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
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

ECB_SERIES_KEY = "D.U2.EUR.4F.KR.DFR.LEV"
ECB_URL = f"https://data-api.ecb.europa.eu/service/data/FM/{ECB_SERIES_KEY}"

dp = DataProvider()
fred = FredDataSource()

print("=" * 90)
print("MERIDIANFX — WALK‑FORWARD: COMPARACIÓN DE MODELOS")
print("=" * 90)
print(f"Pair:              {PAIR}")
print(f"Horizon:           {HORIZON}d")
print(f"Train:             {TRAIN_OBS} obs")
print(f"Validation:        {VAL_OBS} obs")
print(f"Test:              {TEST_OBS} obs")
print(f"Step:              {STEP_OBS} obs")
print("=" * 90)


# ============================================================
# FUNCIONES MACRO
# ============================================================

async def fetch_usd_policy_history(start_date, end_date):
    source = FredDataSource(allow_simulation=False)
    result = await source.fetch_series("DFF", start_date=start_date, end_date=end_date, limit=10000)
    if not result or not result.get("observations"):
        raise RuntimeError("FRED no devolvió observaciones históricas para DFF.")
    df = pd.DataFrame(result["observations"])
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.normalize().astype("datetime64[ns]")
    df["usd_policy_rate"] = pd.to_numeric(df["value"], errors="coerce")
    df = df[["date", "usd_policy_rate"]].dropna().drop_duplicates("date").sort_values("date").reset_index(drop=True)
    if df.empty:
        raise RuntimeError("Serie FRED DFF vacía después del parsing.")
    print(f"   USD policy history: {df['date'].min().date()} → {df['date'].max().date()} ({len(df)} obs)")
    return df


async def fetch_eur_policy_history(start_date, end_date):
    params = {"startPeriod": start_date, "endPeriod": end_date, "format": "csvdata"}
    headers = {"Accept": "text/csv"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(ECB_URL, params=params, headers=headers)
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
    df["eur_policy_rate"] = pd.to_numeric(df[value_col], errors="coerce")
    df = df[["date", "eur_policy_rate"]].dropna().drop_duplicates("date").sort_values("date").reset_index(drop=True)
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


def build_point_in_time_macro(price_index):
    price_dates = pd.DatetimeIndex(pd.to_datetime(price_index)).normalize().astype("datetime64[ns]")
    start_date = (price_dates.min() - pd.Timedelta(days=10)).strftime("%Y-%m-%d")
    end_date = price_dates.max().strftime("%Y-%m-%d")
    print("\n📡 Descargando histórico macro point-in-time...")
    print(f"   Desde: {start_date}")
    print(f"   Hasta: {end_date}")
    usd, eur = get_policy_history_sync(start_date, end_date)
    prices = pd.DataFrame({"date": price_dates}).sort_values("date")
    macro = pd.merge_asof(prices, usd.sort_values("date"), on="date", direction="backward")
    macro = pd.merge_asof(macro.sort_values("date"), eur.sort_values("date"), on="date", direction="backward")
    macro["policy_diff"] = macro["usd_policy_rate"] - macro["eur_policy_rate"]
    # Auditoría
    usd_dates = usd.rename(columns={"date": "usd_observation_date"})
    eur_dates = eur.rename(columns={"date": "eur_observation_date"})
    macro_audit = pd.merge_asof(prices, usd_dates[["usd_observation_date"]], left_on="date", right_on="usd_observation_date", direction="backward")
    macro_audit = pd.merge_asof(macro_audit.sort_values("date"), eur_dates[["eur_observation_date"]], left_on="date", right_on="eur_observation_date", direction="backward")
    macro_audit["usd_lag_days"] = (macro_audit["date"] - macro_audit["usd_observation_date"]).dt.days
    macro_audit["eur_lag_days"] = (macro_audit["date"] - macro_audit["eur_observation_date"]).dt.days
    usd_future = (macro_audit["usd_observation_date"] > macro_audit["date"]).fillna(False)
    eur_future = (macro_audit["eur_observation_date"] > macro_audit["date"]).fillna(False)
    if usd_future.any() or eur_future.any():
        raise RuntimeError("LEAKAGE: observaciones macro futuras utilizadas.")
    print("\n🔍 Auditoría point-in-time")
    print(f"   USD future observations: {int(usd_future.sum())}")
    print(f"   EUR future observations: {int(eur_future.sum())}")
    print(f"   USD max lag: {macro_audit['usd_lag_days'].max()} días")
    print(f"   EUR max lag: {macro_audit['eur_lag_days'].max()} días")
    missing = macro[["usd_policy_rate", "eur_policy_rate", "policy_diff"]].isna().any(axis=1)
    print(f"   Fechas sin macro completo: {int(missing.sum())}")
    return macro.set_index("date")


def prepare_dataset(df):
    df_feat = TechnicalFeatures.generate(df)
    technical_cols = TechnicalFeatures.get_feature_names()
    y_all = TechnicalFeatures.create_target(df_feat, forward_days=HORIZON)
    macro_df = build_point_in_time_macro(df_feat.index)
    macro_aligned = macro_df.reindex(pd.DatetimeIndex(df_feat.index).normalize())
    macro_aligned.index = df_feat.index
    df_feat["policy_diff"] = macro_aligned["policy_diff"]
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
    metrics = {"n_positives": int(np.sum(y_true == 1)), "n_negatives": int(np.sum(y_true == 0)), "n_samples": int(len(y_true))}
    if len(unique_labels) < 2:
        metrics.update({"auc": np.nan, "pr_auc": np.nan, "brier": float(brier_score_loss(y_true, y_proba)), "balanced_accuracy": np.nan, "precision": np.nan, "recall": np.nan, "f1": np.nan, "cm": confusion_matrix(y_true, y_pred).tolist(), "status": "single_class"})
        return metrics
    metrics.update({"auc": float(roc_auc_score(y_true, y_proba)), "pr_auc": float(average_precision_score(y_true, y_proba)), "brier": float(brier_score_loss(y_true, y_proba)), "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)), "precision": float(precision_score(y_true, y_pred, zero_division=0)), "recall": float(recall_score(y_true, y_pred, zero_division=0)), "f1": float(f1_score(y_true, y_pred, zero_division=0)), "cm": confusion_matrix(y_true, y_pred).tolist(), "status": "valid"})
    return metrics


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
# MODELOS
# ============================================================

def build_pipeline(estimator):
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", estimator),
    ])


models = {
    "LogisticRegression": build_pipeline(
        LogisticRegression(
            max_iter=5000,
            random_state=42,
        )
    ),
    "RandomForest": build_pipeline(
        RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
        )
    ),
}

if HAS_XGB:
    models["XGBoost"] = build_pipeline(
        XGBClassifier(
            n_estimators=100,
            max_depth=5,
            random_state=42,
            use_label_encoder=False,
            eval_metric="logloss",
        )
    )


experiments = {
    "technical_only": (X_tech, y_tech),
    "technical_plus_policy": (X_macro, y_macro),
}


all_results = {}

for model_name, model in models.items():
    print(f"\n{'='*90}")
    print(f"MODELO: {model_name}")
    print("=" * 90)
    for exp_name, (X, y) in experiments.items():
        print(f"\n  ── {exp_name} ──")
        results = []
        for fold_config in folds:
            fold_model = copy.deepcopy(model)
            result = run_fold(X, y, fold_config["train_start"], fold_config["train_end"],
                              fold_config["val_start"], fold_config["val_end"],
                              fold_config["test_start"], fold_config["test_end"], fold_model)
            if result is None:
                continue
            result["fold"] = fold_config["fold"]
            results.append(result)
            print(f"    Fold {result['fold']}: AUC={result['test_auc']:.4f} | Brier={result['test_brier']:.4f}")
        all_results[f"{model_name}_{exp_name}"] = results

# ============================================================
# RESUMEN
# ============================================================
print("\n" + "=" * 90)
print("RESUMEN COMPARATIVO")
print("=" * 90)

summary_rows = []
for key, results in all_results.items():
    valid = [r for r in results if r["test_status"] == "valid"]
    if not valid:
        continue
    aucs = [r["test_auc"] for r in valid]
    briers = [r["test_brier"] for r in valid]
    model_name, exp_name = key.split("_", 1)
    summary_rows.append({
        "model": model_name,
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

# Guardar
with open("research_walkforward_models_results.json", "w") as f:
    json.dump(all_results, f, indent=2, default=str)

print("\n📁 Guardado: research_walkforward_models_results.json")
print("=" * 90)
