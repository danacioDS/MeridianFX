"""
Walk-forward validation — parametrizable por par.

Envuelve la lógica de research_walkforward_models.py sin modificarla,
para que el trainer pueda validar un artefacto antes de promoverlo.

NOTA: usa asyncio internamente. Si se llama desde un event loop
activo (por ejemplo, dentro de un async def), hay que await-earla
directamente en lugar de usar asyncio.run.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    brier_score_loss,
    balanced_accuracy_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from backend.layer2.data.provider import DataProvider
from backend.layer2.data.macro.service import MacroService
from backend.layer2.features.technical import TechnicalFeatures

from .schema import ValidationMetrics


HORIZON = 10
PURGE = HORIZON
TRAIN_OBS = 400
VAL_OBS = 100
TEST_OBS = 100
STEP_OBS = 40

# Promotion gate v2 (2026-10-06).
#
# The v1 gate only looked at mean AUC, which is misleading: a model with
# mean AUC 0.64 but 2/6 folds below 0.5 is not reliable. The v2 gate
# adds stability (std across folds), classification accuracy (bal_acc),
# and fold-consistency (% folds above 0.55).
#
# Statuses produced:
#   PROMOTED          → production-grade (all production thresholds pass)
#   APPROVED_RESEARCH → research-grade (research thresholds pass, not prod)
#   REJECTED          → evaluated and did not meet even research thresholds
#   UNAVAILABLE       → could not be evaluated (insufficient data)
#
# Thresholds are PROVISIONAL and should be revisited once more models
# are trained and the distribution of metrics is better understood.
GATE = {
    # --- Production thresholds ---
    "min_val_auc_production": 0.60,
    "min_test_auc_production": 0.60,
    "max_val_std_production": 0.08,
    "min_bal_acc_production": 0.55,
    "min_pct_folds_gt_55_production": 0.83,

    # --- Research thresholds ---
    "min_val_auc_research": 0.55,
    "min_test_auc_research": 0.55,
    "max_val_std_research": 0.10,
    "min_bal_acc_research": 0.50,
    "min_pct_folds_gt_55_research": 0.66,

    # --- Shared ---
    "max_auc_drop": 0.20,
    "max_brier": 0.40,
}


def _build_model() -> Pipeline:
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(
            C=1.0, max_iter=1000, random_state=42, class_weight="balanced",
        )),
    ])


async def _get_policy_diff(pair: str, index: pd.DatetimeIndex) -> pd.Series:
    base, quote = pair.split("/")
    start = (index.min() - pd.Timedelta(days=30)).strftime("%Y-%m-%d")
    end = index.max().strftime("%Y-%m-%d")

    service = MacroService()
    base_df = await service.get_historical_policy_rate(base, start, end)
    quote_df = await service.get_historical_policy_rate(quote, start, end)

    if base_df.empty or quote_df.empty:
        return pd.Series(np.nan, index=index, name="policy_diff")

    base_s = base_df.set_index("date")["policy_rate"].sort_index()
    quote_s = quote_df.set_index("date")["policy_rate"].sort_index()
    merged = pd.merge_asof(
        base_s.to_frame(),
        quote_s.to_frame(),
        left_index=True, right_index=True,
        direction="backward",
        suffixes=("_base", "_quote"),
    )
    diff = (merged["policy_rate_base"] - merged["policy_rate_quote"])
    diff = diff.reindex(index, method="ffill")
    return diff.rename("policy_diff")


async def run_walk_forward(pair: str) -> ValidationMetrics:
    """Corre walk-forward purgado sobre `pair` y aplica el research gate."""
    dp = DataProvider()
    result = dp.get_historical(pair, period="4y")
    df = result["data"]

    df_feat = TechnicalFeatures.generate(df)
    technical_cols = TechnicalFeatures.get_feature_names()

    policy_diff = await _get_policy_diff(pair, df_feat.index)
    df_feat["policy_diff"] = policy_diff

    feature_cols = technical_cols + ["policy_diff"]
    y_all = TechnicalFeatures.create_target(df_feat, forward_days=HORIZON)
    X_all = df_feat[feature_cols]

    valid = X_all.notna().all(axis=1) & y_all.notna()
    X = X_all.loc[valid].copy()
    y = y_all.loc[valid].copy()

    if len(X) < TRAIN_OBS + VAL_OBS + TEST_OBS + 2 * PURGE:
        return ValidationMetrics(
            protocol="walk_forward",
            n_samples=len(X),
            validated=False,
            promotion_status="REJECTED",
            reasons=[f"insufficient samples: {len(X)} < {TRAIN_OBS + VAL_OBS + TEST_OBS + 2 * PURGE}"],
        )

    folds: list[dict[str, Any]] = []
    start = 0
    while start + TRAIN_OBS + 2 * PURGE + VAL_OBS + TEST_OBS <= len(X):
        train = slice(start, start + TRAIN_OBS)
        val = slice(start + TRAIN_OBS + PURGE,
                    start + TRAIN_OBS + PURGE + VAL_OBS)
        test = slice(start + TRAIN_OBS + PURGE + VAL_OBS + PURGE,
                     start + TRAIN_OBS + PURGE + VAL_OBS + PURGE + TEST_OBS)

        X_tr, y_tr = X.iloc[train], y.iloc[train]
        X_va, y_va = X.iloc[val], y.iloc[val]
        X_te, y_te = X.iloc[test], y.iloc[test]

        if len(set(y_tr)) < 2 or len(set(y_te)) < 2 or len(set(y_va)) < 2:
            start += STEP_OBS
            continue

        model = _build_model()
        model.fit(X_tr, y_tr)

        val_proba = model.predict_proba(X_va)[:, 1]
        test_proba = model.predict_proba(X_te)[:, 1]

        try:
            cal = CalibratedClassifierCV(FrozenEstimator(model), method="sigmoid")
            cal.fit(X_va, y_va)
            test_proba_cal = cal.predict_proba(X_te)[:, 1]
        except Exception:
            test_proba_cal = test_proba

        folds.append({
            "val_auc": float(roc_auc_score(y_va, val_proba)),
            "test_auc": float(roc_auc_score(y_te, test_proba)),
            "test_brier": float(brier_score_loss(y_te, test_proba)),
            "cal_brier": float(brier_score_loss(y_te, test_proba_cal)),
            "test_bal_acc": float(balanced_accuracy_score(y_te, (test_proba > 0.5).astype(int))),
            "cal_bal_acc": float(balanced_accuracy_score(y_te, (test_proba_cal > 0.5).astype(int))),
            "n_test": int(len(y_te)),
        })
        start += STEP_OBS

    if not folds:
        return ValidationMetrics(
            protocol="walk_forward",
            n_samples=len(X),
            validated=False,
            promotion_status="REJECTED",
            reasons=["no valid folds generated"],
        )

    # --- Aggregate metrics across folds ---
    val_aucs = [f["val_auc"] for f in folds]
    test_aucs = [f["test_auc"] for f in folds]
    val_auc = float(np.mean(val_aucs))
    test_auc = float(np.mean(test_aucs))
    val_std = float(np.std(val_aucs))
    test_std = float(np.std(test_aucs))
    cal_brier = float(np.mean([f["cal_brier"] for f in folds]))
    cal_bal_acc = float(np.mean([f["cal_bal_acc"] for f in folds]))
    pct_val_gt_55 = sum(1 for a in val_aucs if a > 0.55) / len(val_aucs)
    pct_test_gt_55 = sum(1 for a in test_aucs if a > 0.55) / len(test_aucs)

    reasons: list[str] = []
    warnings: list[str] = []

    # --- Production gate ---
    is_production = (
        val_auc >= GATE["min_val_auc_production"]
        and test_auc >= GATE["min_test_auc_production"]
        and val_std <= GATE["max_val_std_production"]
        and cal_bal_acc >= GATE["min_bal_acc_production"]
        and pct_val_gt_55 >= GATE["min_pct_folds_gt_55_production"]
    )

    # --- Research gate ---
    is_research = (
        val_auc >= GATE["min_val_auc_research"]
        and test_auc >= GATE["min_test_auc_research"]
        and val_std <= GATE["max_val_std_research"]
        and cal_bal_acc >= GATE["min_bal_acc_research"]
        and pct_val_gt_55 >= GATE["min_pct_folds_gt_55_research"]
    )

    # --- Shared warnings (do not block promotion but are recorded) ---
    if (val_auc - test_auc) > GATE["max_auc_drop"]:
        warnings.append(
            f"auc_drop {val_auc - test_auc:.3f} > {GATE['max_auc_drop']}"
        )
    if cal_brier > GATE["max_brier"]:
        warnings.append(
            f"cal_brier {cal_brier:.3f} > {GATE['max_brier']}"
        )

    # --- Reasons (only for the failed level) ---
    if not is_research:
        if val_auc < GATE["min_val_auc_research"]:
            reasons.append(
                f"val_auc {val_auc:.3f} < {GATE['min_val_auc_research']}"
            )
        if test_auc < GATE["min_test_auc_research"]:
            reasons.append(
                f"test_auc {test_auc:.3f} < {GATE['min_test_auc_research']}"
            )
        if val_std > GATE["max_val_std_research"]:
            reasons.append(
                f"val_std {val_std:.3f} > {GATE['max_val_std_research']}"
            )
        if cal_bal_acc < GATE["min_bal_acc_research"]:
            reasons.append(
                f"bal_acc {cal_bal_acc:.3f} < {GATE['min_bal_acc_research']}"
            )
        if pct_val_gt_55 < GATE["min_pct_folds_gt_55_research"]:
            reasons.append(
                f"pct_val_gt_55 {pct_val_gt_55:.2f} < "
                f"{GATE['min_pct_folds_gt_55_research']}"
            )
    elif not is_production:
        # Research-grade but not production: record what is missing
        warnings.append(
            f"research-grade only: val_auc={val_auc:.3f}, "
            f"test_auc={test_auc:.3f}, val_std={val_std:.3f}, "
            f"bal_acc={cal_bal_acc:.3f}, pct_val_gt_55={pct_val_gt_55:.2f}"
        )

    # --- Final status ---
    if is_production:
        status = "PROMOTED"
    elif is_research:
        status = "APPROVED_RESEARCH"
    else:
        status = "REJECTED"

    return ValidationMetrics(
        protocol="walk_forward",
        auc=val_auc,
        bal_acc=cal_bal_acc,
        brier=cal_brier,
        cal_brier=cal_brier,
        n_samples=len(X),
        folds=folds,
        val_auc=val_auc,
        test_auc=test_auc,
        val_std=val_std,
        test_std=test_std,
        pct_val_gt_55=pct_val_gt_55,
        pct_test_gt_55=pct_test_gt_55,
        validated=(status in ("PROMOTED", "APPROVED_RESEARCH")),
        promotion_status=status,
        reasons=reasons,
        warnings=warnings,
    )
