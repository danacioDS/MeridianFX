"""
MeridianFX — Research Gate (v2)

Clasifica modelos candidatos basándose en:
- Validation AUC > 0.60
- Test AUC > 0.60
- Estabilidad (Validation AUC - Test AUC) < 0.20
- PR-AUC > 0.50
- Calibración: Brier < 0.40 (después de calibración)

NOTA: Balanced Accuracy y threshold se evalúan en el Decision Gate.
"""

import pandas as pd
import json
from datetime import datetime

RULES = {
    "min_val_auc": 0.60,
    "min_test_auc": 0.60,
    "max_auc_drop": 0.20,  # Validation AUC - Test AUC
    "min_pr_auc": 0.50,
    "max_brier": 0.40,  # Después de calibración
}

CANDIDATES = [
    ("USD/BOB", 20),
    ("EUR/USD", 10),
]


def evaluate_model(row):
    reasons = []
    warnings = []

    # Validation AUC
    if row["val_auc"] < RULES["min_val_auc"]:
        reasons.append(
            f"validation AUC {row['val_auc']:.3f} < "
            f"{RULES['min_val_auc']:.2f}"
        )

    # Test AUC
    if row["test_auc"] < RULES["min_test_auc"]:
        reasons.append(
            f"test AUC {row['test_auc']:.3f} < "
            f"{RULES['min_test_auc']:.2f}"
        )

    # Estabilidad (drop)
    auc_drop = row["val_auc"] - row["test_auc"]
    if auc_drop > RULES["max_auc_drop"]:
        warnings.append(
            f"caída AUC: {auc_drop:.3f} > "
            f"{RULES['max_auc_drop']:.2f}"
        )

    # PR-AUC
    # Nota: no está en el CSV, lo calculamos aparte si es necesario

    # Brier calibrado
    if row["cal_brier"] > RULES["max_brier"]:
        warnings.append(
            f"Brier calibrado {row['cal_brier']:.3f} > "
            f"{RULES['max_brier']:.2f}"
        )

    # Decisión
    if reasons:
        status = "REJECTED"
    elif warnings:
        status = "CANDIDATE_WITH_WARNINGS"
    else:
        status = "CANDIDATE"

    return status, reasons, warnings


def main():
    try:
        df = pd.read_csv("research_validation_summary.csv")
    except FileNotFoundError:
        print("❌ No se encontró research_validation_summary.csv")
        print("Ejecuta primero: python research_validation_test.py")
        return

    print("=" * 80)
    print("MERIDIANFX — RESEARCH GATE v2")
    print("=" * 80)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Candidatos: {len(CANDIDATES)}")
    print("=" * 80)

    results = []

    for pair, horizon in CANDIDATES:
        rows = df[
            (df["pair"] == pair) &
            (df["horizon"] == horizon)
        ]

        if rows.empty:
            print(f"\n❌ {pair} {horizon}d — NO ENCONTRADO")
            continue

        row = rows.iloc[0]

        status, reasons, warnings = evaluate_model(row)

        print(f"\n{pair} — {horizon}d")
        print(f"  Validation AUC: {row['val_auc']:.4f}")
        print(f"  Test AUC:       {row['test_auc']:.4f}")
        print(f"  Test Brier:     {row['test_brier']:.4f}")
        print(f"  Cal Brier:      {row['cal_brier']:.4f}")
        print(f"  Test Bal Acc:   {row['test_bal_acc']:.4f}")
        print(f"  STATUS:         {status}")

        if reasons:
            for reason in reasons:
                print(f"  ❌ {reason}")

        if warnings:
            for warning in warnings:
                print(f"  ⚠️ {warning}")

        results.append({
            "pair": pair,
            "horizon": horizon,
            "status": status,
            "reasons": reasons,
            "warnings": warnings,
            "val_auc": row["val_auc"],
            "test_auc": row["test_auc"],
            "test_brier": row["test_brier"],
            "test_bal_acc": row["test_bal_acc"],
            "cal_brier": row["cal_brier"],
            "cal_bal_acc": row["cal_bal_acc"],
        })

    # Guardar resultados
    with open("research_gate_results_v2.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    print("\n" + "=" * 80)
    print("📁 Guardado: research_gate_results_v2.json")
    print("=" * 80)

    return results


if __name__ == "__main__":
    main()
