"""
Logistic Regression - Baseline estadístico.
"""
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, brier_score_loss
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np
import joblib
import os

class LogisticModel:
    def __init__(self, model_path: str = None):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        
        if model_path and os.path.exists(model_path):
            try:
                # Cargar el modelo y los metadatos
                saved = joblib.load(model_path)
                if isinstance(saved, dict):
                    self.model = saved['model']
                    self.feature_names = saved.get('feature_names', [])
                    self.scaler = saved.get('scaler', StandardScaler())
                else:
                    self.model = saved
                    # Intentar obtener feature_names del modelo si existe
                    if hasattr(self.model, 'feature_names_in_'):
                        self.feature_names = self.model.feature_names_in_.tolist()
            except Exception as e:
                print(f"⚠️ Error cargando modelo Logistic: {e}")
                self.model = None
                self.feature_names = None
    
    def train(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2):
        """Entrena el modelo de regresión logística y retorna métricas."""
        self.feature_names = X.columns.tolist()
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, shuffle=False
        )
        
        # Escalar features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        self.model = LogisticRegression(
            C=1.0,
            max_iter=1000,
            random_state=42,
            class_weight='balanced'
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        y_pred = self.model.predict(X_test_scaled)
        y_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        
        # Extraer métricas como diccionario simple
        metrics = {
            'accuracy': float(accuracy_score(y_test, y_pred)),
            'auc': float(roc_auc_score(y_test, y_proba)),
            'brier': float(brier_score_loss(y_test, y_proba)),
            'n_samples': int(len(X)),
            'n_features': int(X.shape[1])
        }
        
        print(f"✅ Logistic Regression:")
        print(f"   Accuracy: {metrics['accuracy']:.4f}")
        print(f"   AUC: {metrics['auc']:.4f}")
        print(f"   Brier: {metrics['brier']:.4f}")
        
        return metrics
    
    def predict(self, X: pd.DataFrame) -> dict:
        """Predice dirección y probabilidad."""
        if self.model is None:
            raise ValueError("Modelo no entrenado")
        
        # Usar feature_names si están disponibles
        if self.feature_names:
            X = X[self.feature_names]
        
        X_scaled = self.scaler.transform(X)
        proba = self.model.predict_proba(X_scaled)[0]
        pred = self.model.predict(X_scaled)[0]
        
        direction = "UP" if pred == 1 else "DOWN"
        probability = float(proba[1])
        
        return {
            'direction': direction,
            'probability': probability,
            'raw_prediction': int(pred),
            'probabilities': proba.tolist()
        }
    
    def save(self, path: str):
        """Guarda el modelo y metadatos."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # Guardar como diccionario con metadatos
        saved = {
            'model': self.model,
            'feature_names': self.feature_names,
            'scaler': self.scaler
        }
        joblib.dump(saved, path)
        print(f"✅ Modelo Logistic guardado en {path}")
