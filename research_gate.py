"""
MeridianFX — Research Gate

Clasifica modelos candidatos a partir de resultados
previamente calculados por research_validation_test.py.

IMPORTANTE:
Los modelos aquí marcados como CANDIDATE son candidatos
para producción experimental, NO modelos estadísticamente
validados de forma definitiva.
"""

import pandas as pd
import json
from datetime import datetime

RULES = {
    "min_test_auc": 0.65,
    "min_validation_auc": 0.65,
    "max_brier": 0.70,
    "min_test_balanced_accuracy": 0.55,
}

CANDIDATES = [
    ("USD/BOB", 20),
    ("EUR/USD", 10),
]


def evaluate_model(row):
    reasons = []

    if row["val_auc"] < RULES["min_validation_auc"]:
        reasons.append(
            f"validation AUC {row['val_auc']:.3f} < "
            f"{RULES['min_validation_auc']:.2f}"
        )

    if row["test_auc"] < RULES["min_test_auc"]:
        reasons.append(
            f"test AUC {row['test_auc']:.3f} < "
            f"{RULES['min_test_auc']:.2f}"
        )

    if row["test_brier"] > RULES["max_brier"]:
        reasons.append(
            f"Brier {row['test_brier']:.3f} > "
            f"{RULES['max_brier']:.2f}"
        )

    if row["test_bal_acc"] < RULES["min_test_balanced_accuracy"]:
        reasons.append(
            f"balanced accuracy {row['test_bal_acc']:.3f} < "
            f"{RULES['min_test_balanced_accuracy']:.2f}"
        )

    status = "CANDIDATE" if not reasons else "REJECTED"

    return status, reasons


def main():
    try:
        df = pd.read_csv("research_validation_summary.csv")
    except FileNotFoundError:
        print("❌ No se encontró research_validation_summary.csv")
        print("Ejecuta primero: python research_validation_test.py")
        return

    print("=" * 80)
    print("MERIDIANFX — RESEARCH GATE")
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

        status, reasons = evaluate_model(row)

        print(f"\n{pair} — {horizon}d")
        print(f"  Validation AUC: {row['val_auc']:.4f}")
        print(f"  Test AUC:       {row['test_auc']:.4f}")
        print(f"  Test Brier:     {row['test_brier']:.4f}")
        print(f"  Test Bal Acc:   {row['test_bal_acc']:.4f}")
        print(f"  STATUS:         {status}")

        if reasons:
            for reason in reasons:
                print(f"  ⚠️ {reason}")

        results.append({
            "pair": pair,
            "horizon": horizon,
            "status": status,
            "reasons": reasons,
            "val_auc": row["val_auc"],
            "test_auc": row["test_auc"],
            "test_brier": row["test_brier"],
            "test_bal_acc": row["test_bal_acc"],
            "cal_brier": row["cal_brier"],
            "cal_bal_acc": row["cal_bal_acc"],
        })

    # Guardar resultados del gate
    with open("research_gate_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    print("\n" + "=" * 80)
    print("📁 Guardado: research_gate_results.json")
    print("=" * 80)

    return results


if __name__ == "__main__":
    main()
