"""
SHAP Explainer para XGBoost.
Genera explicaciones de predicciones con SHAP Tree Explainer.
"""
import shap
import pandas as pd
import numpy as np
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

class SHAPExplainer:
    def __init__(self, model, feature_names: list, X_background: pd.DataFrame = None):
        self.model = model
        self.feature_names = feature_names
        self.explainer = None
        self.background = None
        
        if X_background is not None and len(X_background) > 0:
            self.fit(X_background)
    
    def fit(self, X: pd.DataFrame):
        """Ajusta el explainer con datos de background."""
        X = X[self.feature_names].copy().astype(float)
        self.background = X.sample(min(100, len(X)))
        
        # Usar TreeExplainer con parámetros para evitar errores
        try:
            self.explainer = shap.TreeExplainer(
                self.model,
                self.background,
                feature_perturbation="tree_path_dependent"
            )
            print(f"✅ SHAP Explainer ajustado con {len(self.background)} muestras")
        except Exception as e:
            print(f"⚠️ SHAP fit error: {e}")
            # Fallback: intentar sin background
            self.explainer = shap.TreeExplainer(
                self.model,
                feature_perturbation="tree_path_dependent"
            )
            print("✅ SHAP Explainer ajustado sin background")
    
    def explain(self, X: pd.DataFrame) -> dict:
        """Genera explicación SHAP para una muestra."""
        if self.explainer is None:
            return {
                'base_value': 0,
                'base_probability': 0.5,
                'final_probability': 0.5,
                'contributions': [],
                'feature_count': 0,
                'error': 'Explainer not initialized'
            }
        
        X = X[self.feature_names].copy().astype(float)
        
        try:
            shap_values = self.explainer.shap_values(X)
            
            if isinstance(shap_values, list):
                shap_values = shap_values[1]
            
            base_value = float(self.explainer.expected_value)
            if isinstance(base_value, list):
                base_value = float(base_value[1])
            
            contributions = []
            for i, feature in enumerate(self.feature_names):
                val = float(shap_values[0][i]) if len(shap_values.shape) > 1 else float(shap_values[i])
                contributions.append({
                    'feature': feature,
                    'contribution': val,
                    'abs_contribution': abs(val)
                })
            
            contributions.sort(key=lambda x: x['abs_contribution'], reverse=True)
            
            import math
            total_shap = sum([c['contribution'] for c in contributions])
            final_prob = 1 / (1 + math.exp(-(base_value + total_shap)))
            
            return {
                'base_value': base_value,
                'base_probability': 1 / (1 + math.exp(-base_value)),
                'final_probability': final_prob,
                'contributions': contributions[:10],
                'feature_count': len(contributions)
            }
            
        except Exception as e:
            print(f"⚠️ SHAP error: {e}")
            return {
                'base_value': 0,
                'base_probability': 0.5,
                'final_probability': 0.5,
                'contributions': [],
                'feature_count': 0,
                'error': str(e)
            }
    
    def save(self, path: str):
        """Guarda el explainer."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        saved = {
            'explainer': self.explainer,
            'feature_names': self.feature_names,
            'background': self.background
        }
        joblib.dump(saved, path)
        print(f"✅ SHAP Explainer guardado en {path}")
