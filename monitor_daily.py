"""
Monitoreo diario de MeridianFX
Ejecutar automáticamente para registrar predicciones
"""

import json
import os
import sys
from datetime import datetime
from backend.layer2.engine import DecisionEngine

def main():
    print(f"\n📊 MERIDIANFX MONITOR — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Limpiar caché ANTES de crear el engine
    for cf in ["cache/forecast_cache.json", "backend/cache/forecast_cache.json"]:
        if os.path.exists(cf):
            os.remove(cf)
            print(f"🗑️ Caché eliminada: {cf}")

    engine = DecisionEngine()

    # Obtener predicción
    try:
        result = engine.get_forecast("EUR/USD")

        print(f"\n📈 PREDICCIÓN:")
        print(f"   Direction:   {result.get('direction')}")
        print(f"   Probability: {result.get('probability'):.6f}")
        print(f"   Actionable:  {result.get('actionable')}")
        print(f"   Model:       {result.get('model', {}).get('type')}")

        # Guardar en historial
        history_file = "monitor_history.json"
        history = []
        if os.path.exists(history_file):
            with open(history_file, "r") as f:
                history = json.load(f)

        entry = {
            "timestamp": datetime.now().isoformat(),
            "direction": result.get("direction"),
            "probability": result.get("probability"),
            "actionable": result.get("actionable"),
            "model_type": result.get("model", {}).get("type"),
        }
        history.append(entry)

        with open(history_file, "w") as f:
            json.dump(history, f, indent=2)

        print(f"\n✅ Historial guardado: {len(history)} registros")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
