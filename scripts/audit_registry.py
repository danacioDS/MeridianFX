"""
Audit the model registry against the promotion gate.

Usage:
    python scripts/audit_registry.py
    python scripts/audit_registry.py --json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow importing the registry module
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.layer2.models.registry import MIN_AUC, MIN_N_SAMPLES, _passes_gate


def audit(registry_path: Path) -> dict:
    reg = json.load(registry_path.open())
    models = reg.get("models", [])

    rows = []
    for m in models:
        metrics = m.get("metrics", {})
        auc = metrics.get("auc")
        n = metrics.get("n_samples")
        active = m.get("active", False)
        passes = _passes_gate(metrics)

        rows.append({
            "pair": m.get("pair", "?"),
            "model_id": m.get("model_id", "?"),
            "model_type": m.get("model_type", "?"),
            "auc": auc,
            "n_samples": n,
            "active": active,
            "passes_gate": passes,
            "would_be_deployed": active and passes,
        })

    total = len(rows)
    passing = sum(1 for r in rows if r["passes_gate"])
    active = sum(1 for r in rows if r["active"])
    would_deploy = sum(1 for r in rows if r["would_be_deployed"])

    return {
        "thresholds": {"auc": MIN_AUC, "n_samples": MIN_N_SAMPLES},
        "total": total,
        "passing_gate": passing,
        "currently_active": active,
        "would_be_deployed": would_deploy,
        "would_be_deactivated": active - would_deploy,
        "models": rows,
    }


def print_report(report: dict) -> None:
    t = report["thresholds"]
    print("=" * 90)
    print(f"REGISTRY AUDIT — gate: auc >= {t['auc']}, n_samples >= {t['n_samples']}")
    print("=" * 90)
    print()
    print(f"{'PAIR':<10} {'TYPE':<10} {'AUC':<10} {'N':<8} {'ACTIVE':<8} {'PASSES':<8} {'WOULD DEPLOY':<14}")
    print("-" * 90)

    for m in report["models"]:
        auc_str = f"{m['auc']:.4f}" if isinstance(m['auc'], (int, float)) else str(m['auc'])
        n_str = str(m['n_samples']) if m['n_samples'] is not None else "—"
        print(
            f"{m['pair']:<10} {m['model_type']:<10} {auc_str:<10} {n_str:<8} "
            f"{'✅' if m['active'] else '❌':<8} "
            f"{'✅' if m['passes_gate'] else '❌':<8} "
            f"{'✅' if m['would_be_deployed'] else '❌':<14}"
        )

    print()
    print("=" * 90)
    print(f"Total models:              {report['total']}")
    print(f"Pass gate:                 {report['passing_gate']}")
    print(f"Currently active:          {report['currently_active']}")
    print(f"Would be deployed (gate):  {report['would_be_deployed']}")
    print(f"Would be deactivated:      {report['would_be_deactivated']}")
    print("=" * 90)

    if report['would_be_deactivated'] > 0:
        print()
        print(f"⚠️  {report['would_be_deactivated']} model(s) are currently active")
        print(f"   but DO NOT pass the gate. Run scripts/apply_gate.py to fix.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default="models/registry.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = audit(Path(args.registry))

    if args.json:
        print(json.dumps(report, indent=2, default=str))
    else:
        print_report(report)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
