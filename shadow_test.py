"""
Shadow Testing — Logistic_24 vs XGBoost actual
Compara predicciones en tiempo real sin afectar producción
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time

from backend.layer2.engine import DecisionEngine
from backend.layer2.data.provider import DataProvider
from backend.layer2.features.technical import TechnicalFeatures
from backend.layer2.models.xgboost_model import XGBoostModel
from backend.layer2.models.logistic_model import LogisticModel

class ShadowTester:
    def __init__(self):
        self.engine = DecisionEngine()
        self.data_provider = DataProvider()
        self.results = []
        
        # Cargar modelos
        self.xgb_model = self._load_xgboost()
        self.log_model = self._load_logistic()
        
        print("=== SHADOW TESTER INICIALIZADO ===")
        print(f"XGBoost: {'✅ cargado' if self.xgb_model else '❌ no disponible'}")
        print(f"Logistic_24: {'✅ cargado' if self.log_model else '❌ no disponible'}")
    
    def _load_xgboost(self):
        """Carga el modelo XGBoost actual de producción."""
        try:
            # Intentar cargar desde registry
            from backend.layer2.models.registry import ModelRegistry
            registry = ModelRegistry()
            active = registry.get_active("EUR/USD", "xgboost")
            if active:
                path = active.get("path")
                if path:
                    return XGBoostModel(path)
        except:
            pass
        return None
    
    def _load_logistic(self):
        """Carga el modelo Logistic_24."""
        try:
            import joblib
            artifact = joblib.load("models/canonical/logistic_24_20260908_172009.joblib")
            model = artifact["model"]
            
            # Wrapper
            log_model = LogisticModel()
            log_model.model = model
            log_model.scaler = None
            log_model.feature_names = artifact["feature_names"]
            return log_model
        except Exception as e:
            print(f"Error cargando Logistic_24: {e}")
            return None
    
    def get_features(self, pair, period="1y"):
        """Obtiene el vector de features para predicción."""
        result = self.data_provider.get_historical(pair, period=period)
        df = result["data"]
        df_feat = TechnicalFeatures.generate(df)
        
        # Obtener policy_diff (usar el método del Engine)
        # Simplificación: usar valor constante para shadow test
        df_feat["policy_diff"] = -0.345
        
        feature_cols = TechnicalFeatures.get_feature_names() + ["policy_diff"]
        latest = df_feat.iloc[-1:][feature_cols].dropna()
        
        return latest
    
    def predict_xgboost(self, X):
        """Predice con XGBoost."""
        if self.xgb_model is None:
            return None
        try:
            # Asegurar que X tenga las features correctas
            if self.xgb_model.feature_names:
                X = X[self.xgb_model.feature_names]
            return self.xgb_model.predict(X)
        except Exception as e:
            print(f"XGBoost error: {e}")
            return None
    
    def predict_logistic(self, X):
        """Predice con Logistic_24."""
        if self.log_model is None:
            return None
        try:
            return self.log_model.predict(X)
        except Exception as e:
            print(f"Logistic error: {e}")
            return None
    
    def run_shadow_test(self, pair="EUR/USD", n_samples=10):
        """Ejecuta shadow test con datos históricos recientes."""
        print(f"\n=== SHADOW TEST: {pair} ===")
        print(f"Muestras: {n_samples}")
        print("-" * 60)
        
        # Obtener datos históricos
        result = self.data_provider.get_historical(pair, period="1y")
        df = result["data"]
        df_feat = TechnicalFeatures.generate(df)
        
        # Añadir policy_diff
        df_feat["policy_diff"] = -0.345
        
        feature_cols = TechnicalFeatures.get_feature_names() + ["policy_diff"]
        
        # Usar últimas n_samples
        X_all = df_feat[feature_cols].dropna()
        X_all = X_all.tail(n_samples)
        
        results = []
        
        for i in range(len(X_all)):
            X = X_all.iloc[i:i+1]
            
            xgb_pred = self.predict_xgboost(X)
            log_pred = self.predict_logistic(X)
            
            results.append({
                "date": X_all.index[i].strftime("%Y-%m-%d"),
                "xgb_prob": xgb_pred.get("probability", 0.5) if xgb_pred else None,
                "xgb_dir": xgb_pred.get("direction", "N/A") if xgb_pred else None,
                "log_prob": log_pred.get("probability", 0.5) if log_pred else None,
                "log_dir": log_pred.get("direction", "N/A") if log_pred else None,
            })
        
        self.results = results
        self._print_summary()
        self._save_results()
        
        return results
    
    def _print_summary(self):
        """Imprime resumen del shadow test."""
        print("\n=== RESUMEN SHADOW TEST ===")
        print("-" * 60)
        
        for r in self.results:
            print(f"{r['date']}: XGB={r['xgb_prob']:.4f} ({r['xgb_dir']}) | LOG={r['log_prob']:.4f} ({r['log_dir']})")
        
        # Estadísticas
        xgb_probs = [r["xgb_prob"] for r in self.results if r["xgb_prob"] is not None]
        log_probs = [r["log_prob"] for r in self.results if r["log_prob"] is not None]
        
        if xgb_probs and log_probs:
            print(f"\nXGBoost mean prob: {np.mean(xgb_probs):.4f}")
            print(f"Logistic mean prob: {np.mean(log_probs):.4f}")
            
            # Correlación
            min_len = min(len(xgb_probs), len(log_probs))
            if min_len > 1:
                corr = np.corrcoef(xgb_probs[:min_len], log_probs[:min_len])[0, 1]
                print(f"Correlación: {corr:.4f}")
            
            # Acuerdo en dirección
            agreements = sum(1 for r in self.results if r["xgb_dir"] == r["log_dir"])
            print(f"Acuerdo en dirección: {agreements}/{len(self.results)} ({agreements/len(self.results)*100:.1f}%)")
    
    def _save_results(self):
        """Guarda resultados en archivo."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"shadow_test_results_{timestamp}.json"
        with open(path, "w") as f:
            json.dump({
                "timestamp": timestamp,
                "results": self.results,
                "summary": {
                    "xgb_mean": np.mean([r["xgb_prob"] for r in self.results if r["xgb_prob"] is not None]),
                    "log_mean": np.mean([r["log_prob"] for r in self.results if r["log_prob"] is not None]),
                }
            }, f, indent=2)
        print(f"\n✅ Resultados guardados en {path}")

def main():
    tester = ShadowTester()
    
    # Shadow test con datos históricos
    results = tester.run_shadow_test("EUR/USD", n_samples=20)
    
    # También probar predicción en tiempo real
    print("\n=== PREDICCIÓN EN TIEMPO REAL ===")
    print("-" * 60)
    
    X = tester.get_features("EUR/USD")
    
    xgb_pred = tester.predict_xgboost(X)
    log_pred = tester.predict_logistic(X)
    
    if xgb_pred:
        print(f"XGBoost:   prob={xgb_pred.get('probability', 0.5):.4f} dir={xgb_pred.get('direction', 'N/A')}")
    if log_pred:
        print(f"Logistic:  prob={log_pred.get('probability', 0.5):.4f} dir={log_pred.get('direction', 'N/A')}")

if __name__ == "__main__":
    main()
