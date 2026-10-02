"""
Canonical artifact schema — what every .joblib must carry.

Closes F-02 (provenance) and enables F-03 (validation). A third
party can load the .joblib and know which data, which feature
sources, and which validation produced it.
"""
from __future__ import annotations

import hashlib
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


@dataclass
class FeatureProvenance:
    """Where a single feature comes from and what it means."""
    name: str
    source: str
    series: str | None = None
    semantic_label: str = ""
    transform: str = ""
    available: bool = True
    notes: str = ""


@dataclass
class ValidationMetrics:
    """Walk-forward or holdout metrics attached to the artifact."""
    protocol: str = "none"
    auc: float | None = None
    bal_acc: float | None = None
    brier: float | None = None
    cal_brier: float | None = None
    n_samples: int | None = None
    folds: list[dict[str, Any]] = field(default_factory=list)
    validated: bool = False
    promotion_status: str = "REJECTED"
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    notes: str = ""


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=Path(__file__).resolve().parents[3],
            text=True,
        ).strip()
    except Exception:
        return "unknown"


def _tree_clean() -> bool:
    try:
        out = subprocess.check_output(
            ["git", "status", "--porcelain"],
            cwd=Path(__file__).resolve().parents[3],
            text=True,
        )
        return out.strip() == ""
    except Exception:
        return False


def _dataset_hash(X: pd.DataFrame, y: pd.Series) -> str:
    h = hashlib.sha256()
    h.update(str(X.shape).encode())
    h.update("|".join(X.columns.tolist()).encode())
    h.update(np.ascontiguousarray(X.values).tobytes())
    h.update(np.ascontiguousarray(y.values).tobytes())
    return "sha256:" + h.hexdigest()


def build_artifact(
    *,
    pair: str,
    model: Any,
    X: pd.DataFrame,
    y: pd.Series,
    horizon: int,
    feature_provenance: list[FeatureProvenance],
    validation: ValidationMetrics,
    version: str = "1.0.0",
) -> dict[str, Any]:
    """Build the canonical artifact dict — what gets joblib.dump'd."""
    return {
        "model": model,
        "feature_names": X.columns.tolist(),
        "horizon": horizon,
        "pair": pair,
        "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "version": version,
        "training_period": {
            "start": X.index[0].strftime("%Y-%m-%d"),
            "end": X.index[-1].strftime("%Y-%m-%d"),
            "n_samples": len(X),
        },
        "training_samples": len(X),
        "training_commit": _git_commit(),
        "tree_clean": _tree_clean(),
        "dataset_hash": _dataset_hash(X, y),
        "feature_provenance": [asdict(fp) for fp in feature_provenance],
        "validation": asdict(validation),
        "promotion_status": validation.promotion_status,
    }


def validate_artifact(obj: dict[str, Any]) -> list[str]:
    """Return list of missing/invalid fields. Empty = valid."""
    errors: list[str] = []
    required = [
        "model", "feature_names", "horizon", "pair",
        "training_period", "training_commit", "dataset_hash",
        "feature_provenance", "validation", "promotion_status",
    ]
    for k in required:
        if k not in obj:
            errors.append(f"missing: {k}")

    tp = obj.get("training_period")
    if isinstance(tp, dict):
        for k in ("start", "end", "n_samples"):
            if k not in tp:
                errors.append(f"training_period missing: {k}")
    else:
        errors.append("training_period is not a dict")

    val = obj.get("validation")
    if isinstance(val, dict):
        if "validated" not in val:
            errors.append("validation missing: validated")
        if val.get("protocol") == "none":
            errors.append("validation.protocol = none (no metrics attached)")
    else:
        errors.append("validation is not a dict")

    if obj.get("promotion_status") not in ("PROMOTED", "REJECTED", "PENDING"):
        errors.append("promotion_status must be PROMOTED|REJECTED|PENDING")

    return errors
