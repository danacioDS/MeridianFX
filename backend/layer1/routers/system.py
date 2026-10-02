from __future__ import annotations

import json
import os
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


# ═══════════════════════════════════════════════════════════════
# RESEARCH
# ═══════════════════════════════════════════════════════════════

@router.get("/research")
async def research_status() -> dict[str, Any]:
    """
    RESEARCH layer state.

    Findings surfaced:
    - F-02: artifacts missing training_period/provenance
    - F-03: models below random; placeholder metrics; corpus unbound
    - F-04: registry split-brain (only if both files exist)
    """
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
                f"(likely placeholder)"
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


# ═══════════════════════════════════════════════════════════════
# DATA
# ═══════════════════════════════════════════════════════════════

CANONICAL_PAIRS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "USD/CNY", "USD/MXN",
    "USD/BRL", "USD/ARS", "USD/BOB", "USD/CHF",
]

# semántica conocida por moneda, según informe.md §4
_KNOWN_SERIES_SEMANTICS = {
    "USD": ("DFF", "Federal Funds Rate", "OK"),
    "EUR": ("ECB DFR", "ECB Deposit Facility Rate", "OK"),
    "GBP": ("IRLTLT01GBM156N", "long-term rate", "MISLABELED"),
    "JPY": ("IRLTLT01JPM156N", "long-term rate", "MISLABELED"),
    "CHF": ("snboffzisa{LZ}", "SNB policy rate", "STALE"),
    "MXN": ("SF61745", "Banxico target rate", "OK"),
    "BRL": ("INTDSRBRM193N", "long-term rate", "MISLABELED"),
    "CNY": (None, "no historical series", "ABSENT"),
    "ARS": (None, "no historical series", "ABSENT"),
    "BOB": (None, "no historical series", "ABSENT"),
}

_STATUS_RANK = {"OK": 0, "STALE": 1, "MISLABELED": 2, "ABSENT": 3, "UNKNOWN": 4}


@router.get("/data")
async def data_status() -> dict[str, Any]:
    """
    DATA layer state.

    Reads the live CountryMacroRegistry and the known series semantics
    per currency. Checks BOTH base and quote of each pair — a pair is
    only OK if both legs use correct policy-rate semantics.

    Findings surfaced:
    - F-01: long-term rates under a policy_rate label; missing series;
      stale series
    - F-10: MERIDIAN_MODEL_DIR set but unconsumed
    """
    from backend.layer2.data.macro import CountryMacroRegistry

    checks: list[dict[str, Any]] = []
    findings: set[str] = set()
    pair_rows: list[dict[str, Any]] = []

    for pair in CANONICAL_PAIRS:
        base, quote = pair.split("/")
        base_info = _KNOWN_SERIES_SEMANTICS.get(base, (None, "unknown", "UNKNOWN"))
        quote_info = _KNOWN_SERIES_SEMANTICS.get(quote, (None, "unknown", "UNKNOWN"))

        # el estado del par es el peor de los dos
        worst = max(
            [base_info[2], quote_info[2]],
            key=lambda s: _STATUS_RANK.get(s, 5),
        )

        provider = CountryMacroRegistry.get(quote)

        pair_rows.append({
            "pair": pair,
            "base": {
                "currency": base,
                "series": base_info[0],
                "semantic": base_info[1],
                "status": base_info[2],
            },
            "quote": {
                "currency": quote,
                "series": quote_info[0],
                "semantic": quote_info[1],
                "status": quote_info[2],
            },
            "quote_provider": type(provider).__name__ if provider else None,
            "status": worst,
            "has_get_historical": hasattr(provider, "get_historical") if provider else False,
            "has_get_context": hasattr(provider, "get_context") if provider else False,
        })

        if worst in ("MISLABELED", "ABSENT", "STALE"):
            findings.add("F-01")

    mislabeled = [r for r in pair_rows if r["status"] == "MISLABELED"]
    absent = [r for r in pair_rows if r["status"] == "ABSENT"]
    stale = [r for r in pair_rows if r["status"] == "STALE"]
    ok = [r for r in pair_rows if r["status"] == "OK"]

    if mislabeled:
        checks.append({
            "id": "mislabeled_series",
            "status": "FAIL",
            "finding": "F-01",
            "detail": (
                f"{len(mislabeled)} pairs use long-term rates under a "
                f"policy_rate label: {[r['pair'] for r in mislabeled]}"
            ),
        })
    if absent:
        checks.append({
            "id": "absent_series",
            "status": "FAIL",
            "finding": "F-01",
            "detail": (
                f"{len(absent)} pairs have no historical series: "
                f"{[r['pair'] for r in absent]}"
            ),
        })
    if stale:
        checks.append({
            "id": "stale_series",
            "status": "WARN",
            "finding": "F-01",
            "detail": (
                f"{len(stale)} pairs have stale series: "
                f"{[r['pair'] for r in stale]}"
            ),
        })
    if ok:
        checks.append({
            "id": "valid_series",
            "status": "OK",
            "detail": (
                f"{len(ok)} pairs with correct policy-rate semantics "
                f"on both legs: {[r['pair'] for r in ok]}"
            ),
        })

    # MERIDIAN_MODEL_DIR (F-10)
    model_dir = os.environ.get("MERIDIAN_MODEL_DIR")
    consumers: list[str] = []
    backend_dir = REPO_ROOT / "backend"
    if backend_dir.exists():
        for py in backend_dir.rglob("*.py"):
            try:
                if "MERIDIAN_MODEL_DIR" in py.read_text(errors="ignore"):
                    if py.name != "system.py":
                        consumers.append(str(py.relative_to(REPO_ROOT)))
            except OSError:
                pass
    if model_dir and not consumers:
        checks.append({
            "id": "model_dir_unused",
            "status": "WARN",
            "finding": "F-10",
            "detail": (
                f"MERIDIAN_MODEL_DIR={model_dir} is set but no Python "
                f"module reads it"
            ),
        })
        findings.add("F-10")

    layer_status = (
        "DEGRADED" if any(c["status"] == "FAIL" for c in checks)
        else "WARNING" if any(c["status"] == "WARN" for c in checks)
        else "HEALTHY"
    )

    return {
        "layer": "data",
        "status": layer_status,
        "checks": checks,
        "findings": sorted(findings),
        "pairs": pair_rows,
        "summary": {
            "pairs_total": len(pair_rows),
            "pairs_ok": len(ok),
            "pairs_mislabeled": len(mislabeled),
            "pairs_absent": len(absent),
            "pairs_stale": len(stale),
        },
    }
# ═══════════════════════════════════════════════════════════════
# DECISION
# ═══════════════════════════════════════════════════════════════

_TRACED_PAIRS = ["USD/CHF", "USD/MXN", "EUR/USD"]


@router.get("/decision")
async def decision_status(pair: str = "USD/CHF") -> dict[str, Any]:
    """
    DECISION layer state for one pair.

    Reads the live DTO from /v1/canonical/{pair}/decision and surfaces
    the pipeline steps with explicit pass/fail per contract.

    Findings surfaced:
    - F-05: horizon mismatch between trained artifact and served DTO
    - F-08: expected_return is a volatility rescaling, not a forecast
    - F-12: data_quality_score comes from a Stub* registry
    - F-22: fusion declares macro/rag weights but rag is hardcoded 0.0
    - F-06: artifact.model_id does not identify Logistic_24
    """
    from fastapi.testclient import TestClient
    from backend.layer1.main import app as _app

    if "/" not in pair:
        return {"layer": "decision", "status": "UNKNOWN",
                "error": f"invalid pair: {pair}"}

    base, quote = pair.split("/")

    # llamada interna al endpoint canónico — misma lógica, sin duplicar
    client = TestClient(_app)
    resp = client.get(f"/v1/canonical/{base}/{quote}/decision")
    if resp.status_code != 200:
        return {
            "layer": "decision",
            "status": "UNKNOWN",
            "pair": pair,
            "error": f"canonical decision returned {resp.status_code}",
        }
    dto = resp.json()

    # ── extraer campos (rutas defensivas, no asumen estructura) ──
    decision = dto.get("decision") or {}
    economic = dto.get("economic") or {}
    quality = dto.get("quality") or {}
    quality_components = quality.get("components") or {}
    signals = dto.get("signals") or {}
    macro = (signals.get("macro_score") or {}).get("value")
    rag = (signals.get("rag_score") or {}).get("value")
    artifact = dto.get("artifact") or {}

    served_horizon = decision.get("horizon_days") or dto.get("horizon_days")
    trained_horizon = 10   # todos los .joblib tienen horizon: 10

    checks: list[dict[str, Any]] = []
    findings: set[str] = set()

    # ── F-05: horizon match ─────────────────────────────────────
    if served_horizon == trained_horizon:
        checks.append({
            "id": "horizon_match",
            "status": "OK",
            "detail": f"served={served_horizon}d, trained={trained_horizon}d",
        })
    else:
        checks.append({
            "id": "horizon_match",
            "status": "FAIL",
            "finding": "F-05",
            "detail": f"served={served_horizon}d, trained={trained_horizon}d",
        })
        findings.add("F-05")

    # ── F-08: economic layer sanity ─────────────────────────────
    net_return = economic.get("net_return")
    edge_ratio = economic.get("edge_ratio")
    # umbral: un retorno neto esperado > 5% en <=10 días es artefacto
    if net_return is not None and abs(net_return) > 5.0:
        checks.append({
            "id": "economic_layer",
            "status": "FAIL",
            "finding": "F-08",
            "detail": (
                f"net_return={net_return} edge_ratio={edge_ratio} — "
                f"expected_return is a volatility rescaling, not a forecast"
            ),
        })
        findings.add("F-08")
    else:
        checks.append({
            "id": "economic_layer",
            "status": "OK",
            "detail": f"net_return={net_return}",
        })

    # ── F-12: data quality is a constant ────────────────────────
    dq_score = quality_components.get("data_quality_score")
    if dq_score == 0.9:
        checks.append({
            "id": "data_quality_source",
            "status": "WARN",
            "finding": "F-12",
            "detail": (
                f"data_quality_score={dq_score} — comes from a "
                f"StubDataQualityRegistry(0.90), not from real PIT data"
            ),
        })
        findings.add("F-12")
    else:
        checks.append({
            "id": "data_quality_source",
            "status": "OK",
            "detail": f"data_quality_score={dq_score}",
        })

    # ── F-22: fusion weights vs signals ─────────────────────────
    fusion = dto.get("fusion") or {}
    weights = fusion.get("weights") or {}
    declared_rag = weights.get("rag", 0)
    if declared_rag > 0 and rag == 0.0:
        checks.append({
            "id": "fusion_honesty",
            "status": "WARN",
            "finding": "F-22",
            "detail": (
                f"declared rag weight={declared_rag} but rag_score={rag} "
                f"— the weight is decorative"
            ),
        })
        findings.add("F-22")
    else:
        checks.append({
            "id": "fusion_honesty",
            "status": "OK",
            "detail": f"macro={macro} rag={rag}",
        })

    # ── F-06: artifact label ────────────────────────────────────
    model_id = artifact.get("model_id", "")
    if model_id and not model_id.startswith("Logistic_24"):
        checks.append({
            "id": "artifact_label",
            "status": "WARN",
            "finding": "F-06",
            "detail": (
                f"artifact.model_id={model_id!r} — running model is "
                f"Logistic_24, label does not identify it"
            ),
        })
        findings.add("F-06")
    else:
        checks.append({
            "id": "artifact_label",
            "status": "OK",
            "detail": f"model_id={model_id}",
        })

    layer_status = (
        "DEGRADED" if any(c["status"] == "FAIL" for c in checks)
        else "WARNING" if any(c["status"] == "WARN" for c in checks)
        else "HEALTHY"
    )

    return {
        "layer": "decision",
        "status": layer_status,
        "pair": pair,
        "checks": checks,
        "findings": sorted(findings),
        "decision": {
            "direction": decision.get("direction"),
            "confidence": decision.get("confidence"),
            "actionable": decision.get("actionable"),
            "horizon_days": served_horizon,
            "signal_validity": decision.get("signal_validity"),
        },
        "economic": {
            "net_return": net_return,
            "edge_ratio": edge_ratio,
            "position_size": economic.get("position_size"),
            "required_minimum_edge": economic.get("required_minimum_edge"),
        },
        "artifact": {
            "model_id": model_id,
            "model_version": artifact.get("model_version"),
        },
    }
