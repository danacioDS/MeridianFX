"""
Apply the promotion gate retroactively to the registry.

Usage:
    python scripts/apply_gate.py --dry-run
    python scripts/apply_gate.py --apply

This deactivates any model that does not pass the gate.
A backup is written to models/registry.json.backup_<timestamp>.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.layer2.models.registry import MIN_AUC, MIN_N_SAMPLES, _passes_gate


def apply_gate(registry_path: Path, dry_run: bool = True) -> dict:
    reg = json.load(registry_path.open())
    models = reg.get("models", [])
    current = reg.get("current", {})

    to_deactivate = []
    for m in models:
        if not m.get("active", False):
            continue
        if not _passes_gate(m.get("metrics", {})):
            to_deactivate.append(m)

    result = {
        "total": len(models),
        "to_deactivate": len(to_deactivate),
        "deactivated_ids": [m.get("model_id", "?") for m in to_deactivate],
        "dry_run": dry_run,
    }

    if dry_run or not to_deactivate:
        return result

    # Backup
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup = registry_path.with_suffix(f".json.backup_{ts}")
    shutil.copy2(registry_path, backup)
    result["backup"] = str(backup)

    # Apply
    for m in to_deactivate:
        m["active"] = False
        # Remove from current map if present
        key = f"{m['pair']}_{m['model_type']}"
        if current.get(key) == m["model_id"]:
            del current[key]

    registry_path.write_text(json.dumps(reg, indent=2, default=str))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default="models/registry.json")
    parser.add_argument("--dry-run", action="store_true", default=False)
    parser.add_argument("--apply", action="store_true", default=False)
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        print("Specify --dry-run or --apply")
        return 1

    registry_path = Path(args.registry)
    result = apply_gate(registry_path, dry_run=args.dry_run)

    print("=" * 70)
    print(f"APPLY GATE — gate: auc >= {MIN_AUC}, n_samples >= {MIN_N_SAMPLES}")
    print(f"Mode: {'DRY-RUN' if args.dry_run else 'APPLY'}")
    print("=" * 70)
    print(f"Total models:      {result['total']}")
    print(f"To deactivate:     {result['to_deactivate']}")
    if result.get("backup"):
        print(f"Backup:            {result['backup']}")
    print()
    if result["deactivated_ids"]:
        print("Models that do NOT pass the gate:")
        for mid in result["deactivated_ids"]:
            print(f"  - {mid}")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
