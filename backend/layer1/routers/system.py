from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter

router = APIRouter(prefix="/v1/system", tags=["system"])

REPO_ROOT = Path(__file__).resolve().parents[3]


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


@router.get("/research")
async def research_status() -> dict[str, Any]:
    root_reg = _read_json(REPO_ROOT / "models" / "registry.json")
    backend_reg = _read_json(REPO_ROOT / "backend" / "models" / "registry.json")

    checks: list[dict[str, Any]] = []
    findings: set[str] = set()

    # registry parity (F-04)
    if backend_reg is not None and root_reg is not None:
        checks.append({
            "id": "registry_parity",
            "status": "FAIL",
            "finding": "F-04",
            "detail": (
                f"two registries: root={len(root_reg.get('models', []))} models, "
                f"backend={len(backend_reg.get('models', []))} models"
            ),
        })
        findings.add("F-04")
    else:
        checks.append({
            "id": "registry_parity",
            "status": "OK",
            "detail": "single registry: models/registry.json",
        })

    # model quality (F-03)
    models = (root_reg or {}).get("models", [])
    active = [m for m in models if m.get("active")]
    below_random = [
        m for m in models
        if m.get("metrics", {}).get("auc", 1.0) < 0.5
    ]
    round_metrics = [
        m for m in models
        if round(m.get("metrics", {}).get("auc", 0), 2) in (0.45, 0.43, 0.42, 0.44)
    ]

    if below_random:
        checks.append({
            "id": "below_random",
            "status": "FAIL",
            "finding": "F-03",
            "detail": f"{len(below_random)}/{len(models)} models with AUC < 0.5",
        })
        findings.add("F-03")

    if round_metrics:
        checks.append({
            "id": "suspicious_metrics",
            "status": "WARN",
            "finding": "F-03",
            "detail": (
                f"{len(round_metrics)} entries with round AUC "
                f"(likely placeholder): "
                f"{[m['model_id'] for m in round_metrics]}"
            ),
        })
        findings.add("F-03")

    # artifact provenance (F-02)
    artifact_provenance_missing: list[str] = []
    canonical_dir = REPO_ROOT / "models" / "canonical"
    for art in sorted(canonical_dir.glob("logistic_24_*.joblib")):
        try:
            import joblib
            obj = joblib.load(art)
            if not obj.get("training_period"):
                artifact_provenance_missing.append(art.name)
        except Exception:
            pass

    if artifact_provenance_missing:
        checks.append({
            "id": "artifact_provenance",
            "status": "FAIL",
            "finding": "F-02",
            "detail": (
                f"{len(artifact_provenance_missing)} artifacts missing "
                f"training_period/provenance"
            ),
        })
        findings.add("F-02")

    # research corpus (F-03)
    corpus = sorted(REPO_ROOT.glob("research_walkforward*_results.json"))
    if corpus:
        checks.append({
            "id": "corpus_unbound",
            "status": "WARN",
            "finding": "F-03",
            "detail": (
                f"{len(corpus)} walk-forward result files exist but none "
                f"are bound to a promoted artifact"
            ),
        })

    layer_status = (
        "DEGRADED" if any(c["status"] == "FAIL" for c in checks)
        else "WARNING" if any(c["status"] == "WARN" for c in checks)
        else "HEALTHY"
    )

    return {
        "layer": "research",
        "status": layer_status,
        "checks": checks,
        "findings": sorted(findings),
        "summary": {
            "models_total": len(models),
            "models_active": len(active),
            "models_below_random": len(below_random),
            "round_metrics": len(round_metrics),
            "artifacts_missing_provenance": len(artifact_provenance_missing),
            "corpus_files": len(corpus),
            "authoritative_registry": "models/registry.json",
        },
    }
