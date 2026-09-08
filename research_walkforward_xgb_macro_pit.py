"""
MeridianFX — Walk-Forward Validation
Technical vs Technical + Macro Policy Differential

Objetivo:
    Medir si el diferencial histórico de tasas USD-EUR aporta
    información predictiva incremental para EUR/USD a 10 días.

IMPORTANTE:
    - No se utilizan valores macro actuales para fechas históricas.
    - USD: FRED DFF histórico.
    - EUR: ECB Deposit Facility Rate histórico.
    - A cada fecha de precio se asigna únicamente la última
      observación macro disponible <= fecha del precio.
    - No GDP/inflation/unemployment en esta versión.
    - Mismo modelo para ambos experimentos: XGBoost.
"""

import asyncio
import json
import warnings

import httpx
import numpy as np
import pandas as pd
def normalize_dates(df, col="date"):
    df[col] = pd.to_datetime(df[col]).dt.normalize().astype("datetime64[ns]")
    return df

from backend.layer2.data.provider import DataProvider
from backend.layer2.features.technical import TechnicalFeatures
from backend.layer2.data.sources.fred import FredDataSource

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
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
    f1_score,
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
STEP_OBS = 40

OUTPUT_FILE = "research_walkforward_xgb_macro_results.json"

ECB_SERIES_KEY = "D.U2.EUR.4F.KR.DFR.LEV"

# ECB Data API
ECB_URL = (
    "https://data-api.ecb.europa.eu/service/data/"
    f"FM/{ECB_SERIES_KEY}"
)


# ============================================================
# HEADER
# ============================================================

print("=" * 90)
print("MERIDIANFX — WALK-FORWARD: TECHNICAL vs TECHNICAL + MACRO")
print("=" * 90)
print(f"Pair:              {PAIR}")
print(f"Horizon:           {HORIZON}d")
print(f"Train:             {TRAIN_OBS} obs")
print(f"Validation:        {VAL_OBS} obs")
print(f"Test:              {TEST_OBS} obs")
print(f"Step:              {STEP_OBS} obs")
print("=" * 90)


# ============================================================
# HISTÓRICO USD — FRED
# ============================================================


async def fetch_usd_policy_history(start_date, end_date):
    source = FredDataSource(allow_simulation=False)

    result = await source.fetch_series(
        "DFF",
        start_date=start_date,
        end_date=end_date,
        limit=10000,
    )

    if not result or not result.get("observations"):
        raise RuntimeError(
            "FRED no devolvió observaciones históricas para DFF. "
            "Verifica FRED_API_KEY."
        )

    df = pd.DataFrame(result["observations"])

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
    ).dt.normalize().astype("datetime64[ns]")

    df["usd_policy_rate"] = pd.to_numeric(
        df["value"],
        errors="coerce",
    )

    df = (
        df[["date", "usd_policy_rate"]]
        .dropna()
        .drop_duplicates("date")
        .sort_values("date")
        .reset_index(drop=True)
    )

    if df.empty:
        raise RuntimeError(
            "Serie FRED DFF vacía después del parsing."
        )

    print(
        f"   USD policy history: "
        f"{df['date'].min().date()} → "
        f"{df['date'].max().date()} "
        f"({len(df)} obs)"
    )

    return df


async def fetch_eur_policy_history(start_date, end_date):
    params = {
        "startPeriod": start_date,
        "endPeriod": end_date,
        "format": "csvdata",
    }

    headers = {
        "Accept": "text/csv",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            ECB_URL,
            params=params,
            headers=headers,
        )

    if response.status_code != 200:
        raise RuntimeError(
            f"ECB API error {response.status_code}: "
            f"{response.text[:500]}"
        )

    text = response.text

    if not text.strip():
        raise RuntimeError(
            "ECB devolvió una respuesta CSV vacía."
        )

    from io import StringIO

    df = pd.read_csv(StringIO(text))

    if df.empty:
        raise RuntimeError(
            "ECB devolvió 0 observaciones."
        )

    df.columns = [
        str(c).strip()
        for c in df.columns
    ]

    time_col = next(
        (
            c for c in df.columns
            if c.upper() in {
                "TIME_PERIOD",
                "TIME PERIOD",
                "DATE",
            }
        ),
        None,
    )

    value_col = next(
        (
            c for c in df.columns
            if c.upper() in {
                "OBS_VALUE",
                "OBS VALUE",
                "VALUE",
            }
        ),
        None,
    )

    if time_col is None or value_col is None:
        raise RuntimeError(
            "No se encontraron columnas "
            "TIME_PERIOD/OBS_VALUE en respuesta ECB. "
            f"Columnas: {list(df.columns)}"
        )

    # IMPORTANTE:
    # Primero convertimos TIME_PERIOD -> date.
    # Recién después normalizamos el dtype.
    df["date"] = pd.to_datetime(
        df[time_col],
        errors="coerce",
    ).dt.normalize().astype("datetime64[ns]")

    df["eur_policy_rate"] = pd.to_numeric(
        df[value_col],
        errors="coerce",
    )

    df = (
        df[["date", "eur_policy_rate"]]
        .dropna()
        .drop_duplicates("date")
        .sort_values("date")
        .reset_index(drop=True)
    )

    if df.empty:
        raise RuntimeError(
            "Serie ECB vacía después del parsing."
        )

    print(
        f"   EUR policy history: "
        f"{df['date'].min().date()} → "
        f"{df['date'].max().date()} "
        f"({len(df)} obs)"
    )

    return df


def get_policy_history_sync(start_date, end_date):
    """
    Obtiene USD + EUR policy rates históricas.
    """

    async def _fetch():
        usd, eur = await asyncio.gather(
            fetch_usd_policy_history(start_date, end_date),
            fetch_eur_policy_history(start_date, end_date),
        )
        return usd, eur

    return asyncio.run(_fetch())


def build_point_in_time_macro(price_index):
    """
    Construye el policy_diff histórico usando el cálculo canónico
    de MacroDifferentialProvider.

    Para cada fecha de precio t:

        USD(t) = última observación USD <= t
        EUR(t) = última observación EUR <= t

    El diferencial y su normalización son exactamente los mismos
    utilizados por producción.

    No se utilizan observaciones macro posteriores a la fecha
    de precio.
    """

    if len(price_index) == 0:
        raise ValueError("price_index vacío.")

    price_dates = pd.DatetimeIndex(
        pd.to_datetime(price_index)
    ).normalize()

    start_date = (
        price_dates.min() - pd.Timedelta(days=10)
    ).strftime("%Y-%m-%d")

    end_date = price_dates.max().strftime("%Y-%m-%d")

    print("\n📊 HISTÓRICO MACRO PIT")
    print(f"   Desde: {start_date}")
    print(f"   Hasta: {end_date}")

    usd, eur = get_policy_history_sync(
        start_date,
        end_date,
    )
    
    # Renombrar columnas para MacroDifferentialProvider.calculate_historical()
    usd = usd.rename(columns={"usd_policy_rate": "policy_rate"})
    eur = eur.rename(columns={"eur_policy_rate": "policy_rate"})

    # --------------------------------------------------------
    # Normalización explícita de fechas
    # --------------------------------------------------------

    usd = usd.copy()
    eur = eur.copy()

    usd["date"] = (
        pd.to_datetime(usd["date"])
        .dt.normalize()
        .astype("datetime64[ns]")
    )

    eur["date"] = (
        pd.to_datetime(eur["date"])
        .dt.normalize()
        .astype("datetime64[ns]")
    )

    price_dates = (
        pd.DatetimeIndex(price_dates)
        .astype("datetime64[ns]")
    )

    # --------------------------------------------------------
    # Cálculo CANÓNICO de policy_diff
    # --------------------------------------------------------

    from backend.layer2.data.macro.differential_provider import (
        MacroDifferentialProvider,
    )

    policy_diff = MacroDifferentialProvider.calculate_historical(
        base_currency="USD",
        quote_currency="EUR",
        base_series=usd,
        quote_series=eur,
        price_dates=price_dates,
    )

    # --------------------------------------------------------
    # Auditoría PIT independiente
    # --------------------------------------------------------

    prices = pd.DataFrame({
        "date": price_dates,
    }).sort_values("date")

    usd_audit = usd.rename(
        columns={"date": "usd_observation_date"}
    )

    eur_audit = eur.rename(
        columns={"date": "eur_observation_date"}
    )

    macro_audit = pd.merge_asof(
        prices,
        usd_audit[["usd_observation_date"]],
        left_on="date",
        right_on="usd_observation_date",
        direction="backward",
    )

    macro_audit = pd.merge_asof(
        macro_audit.sort_values("date"),
        eur_audit[["eur_observation_date"]],
        left_on="date",
        right_on="eur_observation_date",
        direction="backward",
    )

    macro_audit["usd_lag_days"] = (
        macro_audit["date"]
        - macro_audit["usd_observation_date"]
    ).dt.days

    macro_audit["eur_lag_days"] = (
        macro_audit["date"]
        - macro_audit["eur_observation_date"]
    ).dt.days

    usd_future = (
        macro_audit["usd_observation_date"]
        > macro_audit["date"]
    )

    eur_future = (
        macro_audit["eur_observation_date"]
        > macro_audit["date"]
    )

    print("\n🔍 AUDITORÍA PIT")

    print(
        f"   USD future observations: "
        f"{int(usd_future.sum())}"
    )

    print(
        f"   EUR future observations: "
        f"{int(eur_future.sum())}"
    )

    print(
        f"   USD max lag: "
        f"{macro_audit['usd_lag_days'].max()} días"
    )

    print(
        f"   EUR max lag: "
        f"{macro_audit['eur_lag_days'].max()} días"
    )

    missing_macro = policy_diff.isna()

    print(
        f"   Fechas sin policy_diff: "
        f"{int(missing_macro.sum())}"
    )

    print(
        f"   Policy_diff valores únicos: "
        f"{policy_diff.nunique()}"
    )

    if usd_future.any() or eur_future.any():
        raise RuntimeError(
            "PIT violation: se detectaron observaciones futuras."
        )

    # Convertir Series a DataFrame con columna 'policy_diff'
    # Convertir Series a DataFrame con columna 'policy_diff'
    return policy_diff.to_frame("policy_diff")


# ============================================================
# PREPARACIÓN DE FEATURES
# ============================================================

def prepare_dataset(df):
    """
    Genera dos datasets idénticos salvo por la inclusión
    del diferencial de política monetaria.

    A = Technical only
    B = Technical + policy_diff
    """

    df_feat = TechnicalFeatures.generate(df)

    technical_cols = TechnicalFeatures.get_feature_names()

    # Crear target antes de eliminar filas.
    y_all = TechnicalFeatures.create_target(
        df_feat,
        forward_days=HORIZON,
    )

    # --------------------------------------------------------
    # Macro histórico
    # --------------------------------------------------------

    macro_df = build_point_in_time_macro(
        df_feat.index
    )

    macro_aligned = macro_df.reindex(
        pd.DatetimeIndex(df_feat.index).normalize()
    )

    macro_aligned.index = df_feat.index

    # Añadir únicamente policy_diff.
    df_feat["policy_diff"] = macro_aligned["policy_diff"]

    # --------------------------------------------------------
    # Technical only
    # --------------------------------------------------------

    X_technical_all = df_feat[technical_cols]

    valid_technical = (
        X_technical_all.notna().all(axis=1)
        & y_all.notna()
    )

    X_technical = X_technical_all.loc[
        valid_technical
    ].copy()

    y_technical = y_all.loc[
        valid_technical
    ].copy()

    # --------------------------------------------------------
    # Technical + Macro
    # --------------------------------------------------------

    macro_cols = ["policy_diff"]

    X_macro_all = df_feat[
        technical_cols + macro_cols
    ]

    valid_macro = (
        X_macro_all.notna().all(axis=1)
        & y_all.notna()
    )

    X_macro = X_macro_all.loc[
        valid_macro
    ].copy()

    y_macro = y_all.loc[
        valid_macro
    ].copy()

    return (
        X_technical,
        y_technical,
        X_macro,
        y_macro,
        technical_cols,
        macro_cols,
    )


# ============================================================
# MÉTRICAS
# ============================================================

def compute_metrics(y_true, y_pred, y_proba):
    unique_labels = np.unique(y_true)

    metrics = {
        "n_positives": int(np.sum(y_true == 1)),
        "n_negatives": int(np.sum(y_true == 0)),
        "n_samples": int(len(y_true)),
    }

    if len(unique_labels) < 2:
        metrics.update({
            "auc": np.nan,
            "pr_auc": np.nan,
            "brier": float(
                brier_score_loss(
                    y_true,
                    y_proba,
                )
            ),
            "balanced_accuracy": np.nan,
            "precision": np.nan,
            "recall": np.nan,
            "f1": np.nan,
            "cm": confusion_matrix(
                y_true,
                y_pred,
            ).tolist(),
            "status": "single_class",
        })

        return metrics

    metrics.update({
        "auc": float(
            roc_auc_score(
                y_true,
                y_proba,
            )
        ),
        "pr_auc": float(
            average_precision_score(
                y_true,
                y_proba,
            )
        ),
        "brier": float(
            brier_score_loss(
                y_true,
                y_proba,
            )
        ),
        "balanced_accuracy": float(
            balanced_accuracy_score(
                y_true,
                y_pred,
            )
        ),
        "precision": float(
            precision_score(
                y_true,
                y_pred,
                zero_division=0,
            )
        ),
        "recall": float(
            recall_score(
                y_true,
                y_pred,
                zero_division=0,
            )
        ),
        "f1": float(
            f1_score(
                y_true,
                y_pred,
                zero_division=0,
            )
        ),
        "cm": confusion_matrix(
            y_true,
            y_pred,
        ).tolist(),
        "status": "valid",
    })

    return metrics


# ============================================================
# MODELO
# ============================================================


def build_model():
    return Pipeline([
        (
            "imputer",
            SimpleImputer(strategy="median"),
        ),
        (
            "scaler",
            StandardScaler(),
        ),
        (
            "model",
            XGBClassifier(
                n_estimators=100,
                learning_rate=0.05,
                max_depth=5,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                eval_metric="logloss",
                enable_categorical=False,
            ),
        ),
    ])



# ============================================================
# WALK-FORWARD
# ============================================================

def run_fold(
    X,
    y,
    train_start,
    train_end,
    val_start,
    val_end,
    test_start,
    test_end,
):
    X_train = X.iloc[train_start:train_end]
    y_train = y.iloc[train_start:train_end]

    X_val = X.iloc[val_start:val_end]
    y_val = y.iloc[val_start:val_end]

    X_test = X.iloc[test_start:test_end]
    y_test = y.iloc[test_start:test_end]

    if (
        len(X_train) < 100
        or len(X_val) < 20
        or len(X_test) < 20
    ):
        return None

    if len(np.unique(y_train)) < 2:
        return None

    if len(np.unique(y_val)) < 2:
        return None

    model = build_model()

    model.fit(
        X_train,
        y_train,
    )

    # --------------------------------------------------------
    # Raw
    # --------------------------------------------------------

    proba_test = model.predict_proba(
        X_test
    )[:, 1]

    pred_test = (
        proba_test >= 0.5
    ).astype(int)

    # --------------------------------------------------------
    # Calibration
    # --------------------------------------------------------

    calibrator = CalibratedClassifierCV(
        FrozenEstimator(model),
        method="sigmoid",
    )

    calibrator.fit(
        X_val,
        y_val,
    )

    proba_cal = calibrator.predict_proba(
        X_test
    )[:, 1]

    pred_cal = (
        proba_cal >= 0.5
    ).astype(int)

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    raw = compute_metrics(
        y_test,
        pred_test,
        proba_test,
    )

    calibrated = compute_metrics(
        y_test,
        pred_cal,
        proba_cal,
    )

    return {
        "n_train": len(X_train),
        "n_val": len(X_val),
        "n_test": len(X_test),

        "train_start_date": str(X_train.index[0]),
        "train_end_date": str(X_train.index[-1]),

        "val_start_date": str(X_val.index[0]),
        "val_end_date": str(X_val.index[-1]),

        "test_start_date": str(X_test.index[0]),
        "test_end_date": str(X_test.index[-1]),

        "test_auc": raw["auc"],
        "test_brier": raw["brier"],
        "test_bal_acc": raw["balanced_accuracy"],

        "cal_auc": calibrated["auc"],
        "cal_brier": calibrated["brier"],
        "cal_bal_acc": calibrated["balanced_accuracy"],

        "test_status": raw["status"],

        "test_up": raw["n_positives"],
        "test_down": raw["n_negatives"],
    }


# ============================================================
# GENERAR FOLDS
# ============================================================

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

        folds.append({
            "fold": len(folds) + 1,
            "train_start": train_start,
            "train_end": train_end,
            "val_start": val_start,
            "val_end": val_end,
            "test_start": test_start,
            "test_end": test_end,
        })

        current_start += STEP_OBS

    return folds


# ============================================================
# EJECUTAR EXPERIMENTO
# ============================================================

print("\n📥 Cargando datos...")

dp = DataProvider()

result = dp.get_historical(
    PAIR,
    period="4y",
)

df = result["data"]

print(
    f"   Filas originales: {len(df)}"
)

print(
    f"   Periodo: "
    f"{df.index.min()} → {df.index.max()}"
)


print("\n⚙️ Generando technical + macro point-in-time...")

(
    X_technical,
    y_technical,
    X_macro,
    y_macro,
    technical_cols,
    macro_cols,
) = prepare_dataset(df)


print("\n📊 Dataset Technical")
print(
    f"   Filas válidas: {len(X_technical)}"
)
print(
    f"   Features: {len(technical_cols)}"
)
print(
    f"   Primera fecha: {X_technical.index[0]}"
)
print(
    f"   Última fecha: {X_technical.index[-1]}"
)


print("\n📊 Dataset Technical + Macro")
print(
    f"   Filas válidas: {len(X_macro)}"
)
print(
    f"   Features: "
    f"{len(technical_cols) + len(macro_cols)}"
)
print(
    f"   Macro: {macro_cols}"
)
print(
    f"   Primera fecha: {X_macro.index[0]}"
)
print(
    f"   Última fecha: {X_macro.index[-1]}"
)


# ============================================================
# ALINEACIÓN TEMPORAL
# ============================================================

# Para comparar justamente ambos experimentos, usamos solamente
# las fechas presentes en ambos datasets.

common_dates = X_technical.index.intersection(
    X_macro.index
)

X_technical = X_technical.loc[
    common_dates
].sort_index()

y_technical = y_technical.loc[
    common_dates
].sort_index()

X_macro = X_macro.loc[
    common_dates
].sort_index()

y_macro = y_macro.loc[
    common_dates
].sort_index()


if not y_technical.equals(y_macro):
    raise RuntimeError(
        "Los targets Technical y Macro no están alineados."
    )


n = len(common_dates)

print("\n🔗 Dataset común para comparación")
print(
    f"   Filas: {n}"
)
print(
    f"   Primera fecha: {common_dates[0]}"
)
print(
    f"   Última fecha: {common_dates[-1]}"
)


# ============================================================
# FOLDS
# ============================================================

folds = generate_folds(n)

print(
    f"\n📊 Folds generados: {len(folds)}"
)


# ============================================================
# EXPERIMENTOS
# ============================================================

experiments = {
    "technical_only": (
        X_technical,
        y_technical,
    ),
    "technical_plus_policy_diff": (
        X_macro,
        y_macro,
    ),
}


all_results = {}


for experiment_name, (X, y) in experiments.items():

    print("\n" + "=" * 90)
    print(
        f"EXPERIMENTO: {experiment_name}"
    )
    print("=" * 90)

    results = []

    for fold_config in folds:

        fold_num = fold_config["fold"]

        result = run_fold(
            X,
            y,
            fold_config["train_start"],
            fold_config["train_end"],
            fold_config["val_start"],
            fold_config["val_end"],
            fold_config["test_start"],
            fold_config["test_end"],
        )

        if result is None:
            continue

        result["fold"] = fold_num

        results.append(result)

        print(
            f"   Fold {fold_num}: "
            f"{result['test_start_date'][:10]} → "
            f"{result['test_end_date'][:10]} | "
            f"AUC={result['test_auc']:.4f} | "
            f"Brier={result['test_brier']:.4f} | "
            f"Cal AUC={result['cal_auc']:.4f} | "
            f"Cal Brier={result['cal_brier']:.4f}"
        )

    all_results[experiment_name] = results


# ============================================================
# RESUMEN
# ============================================================

print("\n" + "=" * 90)
print("RESUMEN: TECHNICAL vs TECHNICAL + POLICY DIFFERENTIAL")
print("=" * 90)


summary_rows = []


for experiment_name, results in all_results.items():

    valid = [
        r for r in results
        if r["test_status"] == "valid"
    ]

    if not valid:
        continue

    aucs = np.array([
        r["test_auc"]
        for r in valid
    ])

    briers = np.array([
        r["test_brier"]
        for r in valid
    ])

    cal_aucs = np.array([
        r["cal_auc"]
        for r in valid
    ])

    cal_briers = np.array([
        r["cal_brier"]
        for r in valid
    ])

    summary_rows.append({
        "experiment": experiment_name,
        "n_folds": len(valid),

        "auc_mean": float(np.mean(aucs)),
        "auc_std": float(np.std(aucs)),
        "auc_min": float(np.min(aucs)),
        "auc_max": float(np.max(aucs)),

        "brier_mean": float(np.mean(briers)),

        "cal_auc_mean": float(
            np.mean(cal_aucs)
        ),

        "cal_brier_mean": float(
            np.mean(cal_briers)
        ),

        "pct_auc_gt_050": float(
            100 * np.mean(aucs > 0.50)
        ),

        "pct_auc_gt_060": float(
            100 * np.mean(aucs > 0.60)
        ),
    })


summary_df = pd.DataFrame(
    summary_rows
)

if not summary_df.empty:

    print(
        summary_df.to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}",
        )
    )

    # --------------------------------------------------------
    # Incremental effect
    # --------------------------------------------------------

    if len(summary_df) == 2:

        tech = summary_df[
            summary_df["experiment"]
            == "technical_only"
        ].iloc[0]

        macro = summary_df[
            summary_df["experiment"]
            == "technical_plus_policy_diff"
        ].iloc[0]

        print("\n📈 EFECTO INCREMENTAL DEL POLICY DIFFERENTIAL")

        print(
            f"   Δ AUC mean: "
            f"{macro['auc_mean'] - tech['auc_mean']:+.4f}"
        )

        print(
            f"   Δ AUC std:  "
            f"{macro['auc_std'] - tech['auc_std']:+.4f}"
        )

        print(
            f"   Δ Brier:    "
            f"{macro['brier_mean'] - tech['brier_mean']:+.4f}"
        )

        print(
            f"   Δ Cal AUC:  "
            f"{macro['cal_auc_mean'] - tech['cal_auc_mean']:+.4f}"
        )

        print(
            f"   Δ Cal Brier:"
            f" {macro['cal_brier_mean'] - tech['cal_brier_mean']:+.4f}"
        )


# ============================================================
# GUARDAR
# ============================================================

output = {
    "protocol": {
        "pair": PAIR,
        "horizon": HORIZON,
        "purge": PURGE,
        "train_obs": TRAIN_OBS,
        "val_obs": VAL_OBS,
        "test_obs": TEST_OBS,
        "step_obs": STEP_OBS,
        "model": "LogisticRegression",
        "calibration": "sigmoid_frozen_estimator",
    },

    "macro": {
        "usd_source": "FRED DFF",
        "eur_source": "ECB Deposit Facility Rate",
        "eur_series": ECB_SERIES_KEY,
        "alignment": "merge_asof backward",
        "forbidden_future_observations": True,
        "features": ["policy_diff"],
    },

    "experiments": all_results,

    "summary": summary_rows,
}


with open(
    OUTPUT_FILE,
    "w",
) as f:
    json.dump(
        output,
        f,
        indent=2,
        default=str,
    )


print(
    f"\n📁 Guardado: {OUTPUT_FILE}"
)

print("=" * 90)
# [PATCH] Corregir merge_asof dtype mismatch
# Sobrescribir las funciones fetch con conversión explícita a datetime64[ns]

import pandas as pd
from datetime import datetime

def normalize_dates(df, col="date"):
    """Normaliza columna de fechas a datetime64[ns]."""
    df[col] = pd.to_datetime(df[col]).dt.normalize().astype("datetime64[ns]")
    return df

# Parchear las funciones existentes mediante monkey-patch
# (Esto se ejecuta después de las definiciones originales)
