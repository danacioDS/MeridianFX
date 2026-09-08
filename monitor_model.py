"""
Monitor de modelo Logistic_24 en producción
Verifica:
1. Predicciones actuales
2. Distribución de probabilidades
3. Policy_diff en tiempo real
4. Estado del modelo
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from backend.layer2.engine import DecisionEngine

class ModelMonitor:
    def __init__(self):
        self.engine = DecisionEngine()
        self.history = []
    
    def get_current_forecast(self, pair="EUR/USD"):
        """Obtiene la predicción actual."""
        # Forzar recarga eliminando caché
        import os
        for cf in ["cache/forecast_cache.json", "backend/cache/forecast_cache.json"]:
            if os.path.exists(cf):
                os.remove(cf)
        return self.engine.get_forecast(pair)
    
    def get_model_status(self):
        """Obtiene el estado del modelo."""
        log_model = self.engine._get_model_for_pair("EUR/USD", "logistic")
        if log_model and log_model.model:
            return {
                "loaded": True,
                "type": "Logistic_24",
                "features": len(log_model.feature_names) if log_model.feature_names else 0,
                "last_feature": log_model.feature_names[-1] if log_model.feature_names else None,
            }
        return {"loaded": False}
    
    def run_check(self, pair="EUR/USD"):
        """Ejecuta un chequeo completo."""
        status = self.get_model_status()
        forecast = self.get_current_forecast(pair)
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "pair": pair,
            "model": status,
            "forecast": {
                "direction": forecast.get("direction"),
                "probability": forecast.get("probability"),
                "actionable": forecast.get("actionable"),
            },
            "policy_diff": forecast.get("policy_diff"),
        }
        
        self.history.append(result)
        return result
    
    def print_report(self, result):
        """Imprime un reporte del chequeo."""
        print("\n" + "=" * 60)
        print(f"📊 MONITOREO MERIDIANFX — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        print(f"Pair:           {result['pair']}")
        print(f"Modelo:         {result['model']['type']}")
        print(f"Features:       {result['model']['features']}")
        print(f"Última feature: {result['model']['last_feature']}")
        print("-" * 60)
        print(f"Direction:      {result['forecast']['direction']}")
        print(f"Probability:    {result['forecast']['probability']:.6f}")
        print(f"Actionable:     {result['forecast']['actionable']}")
        print(f"Policy diff:    {result['policy_diff']}")
        print("=" * 60)

def main():
    monitor = ModelMonitor()
    
    # Chequeo actual
    result = monitor.run_check("EUR/USD")
    monitor.print_report(result)
    
    # Guardar historial
    with open("monitor_history.json", "w") as f:
        json.dump(monitor.history, f, indent=2)
    print("\n✅ Historial guardado en monitor_history.json")

if __name__ == "__main__":
    main()
