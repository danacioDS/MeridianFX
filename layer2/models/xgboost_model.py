import xgboost as xgb
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score, brier_score_loss
import joblib
import os

class XGBoostModel:
    def __init__(self, model_path: str = None):
        self.model = None
        self.feature_names = None
        
        if model_path and os.path.exists(model_path):
            try:
                saved = joblib.load(model_path)
                if isinstance(saved, dict):
                    self.model = saved['model']
                    self.feature_names = saved.get('feature_names', [])
                else:
                    self.model = saved
                    if hasattr(self.model, 'feature_names_in_'):
                        self.feature_names = self.model.feature_names_in_.tolist()
            except Exception as e:
                print(f"⚠️ Error cargando modelo XGBoost: {e}")
                self.model = None
                self.feature_names = None
    
    def train(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2):
        """Entrena el modelo XGBoost y retorna métricas."""
        self.feature_names = X.columns.tolist()
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, shuffle=False
        )
        
        # Forzar todas las features como numéricas
        X_train = X_train.astype(float)
        X_test = X_test.astype(float)
        
        self.model = xgb.XGBClassifier(
            n_estimators=100,
            learning_rate=0.05,
            max_depth=5,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric='logloss',
            enable_categorical=False  # Forzar que no use categorical
        )
        
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_train, y_train), (X_test, y_test)],
            verbose=True
        )
        
        y_pred = self.model.predict(X_test)
        y_proba = self.model.predict_proba(X_test)[:, 1]
        
        metrics = {
            'accuracy': float(accuracy_score(y_test, y_pred)),
            'auc': float(roc_auc_score(y_test, y_proba)),
            'brier': float(brier_score_loss(y_test, y_proba)),
            'n_samples': int(len(X)),
            'n_features': int(X.shape[1])
        }
        
        print(f"✅ XGBoost:")
        print(f"   Accuracy: {metrics['accuracy']:.4f}")
        print(f"   AUC: {metrics['auc']:.4f}")
        print(f"   Brier: {metrics['brier']:.4f}")
        print(classification_report(y_test, y_pred))
        
        return metrics
    
    def predict(self, X: pd.DataFrame) -> dict:
        """Predice dirección y probabilidad."""
        if self.model is None:
            raise ValueError("Modelo no entrenado")
        
        if self.feature_names:
            X = X[self.feature_names]
        
        # Forzar float
        X = X.astype(float)
        
        proba = self.model.predict_proba(X)[0]
        pred = self.model.predict(X)[0]
        
        direction = "UP" if pred == 1 else "DOWN"
        probability = float(max(proba))
        
        return {
            'direction': direction,
            'probability': probability,
            'raw_prediction': int(pred),
            'probabilities': proba.tolist()
        }
    
    def predict_batch(self, X: pd.DataFrame) -> pd.DataFrame:
        """Predice para múltiples muestras."""
        if self.model is None:
            raise ValueError("Modelo no entrenado")
        
        if self.feature_names:
            X = X[self.feature_names]
        
        X = X.astype(float)
        proba = self.model.predict_proba(X)
        pred = self.model.predict(X)
        
        return pd.DataFrame({
            'prediction': pred,
            'probability_up': proba[:, 1],
            'probability_down': proba[:, 0]
        })
    
    def save(self, path: str):
        """Guarda el modelo y metadatos."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        saved = {
            'model': self.model,
            'feature_names': self.feature_names
        }
        joblib.dump(saved, path)
        print(f"✅ Modelo XGBoost guardado en {path}")
    
    def feature_importance(self) -> pd.DataFrame:
        """Retorna importancia de características."""
        if self.model is None:
            raise ValueError("Modelo no entrenado")
        
        importance = self.model.feature_importances_
        return pd.DataFrame({
            'feature': self.feature_names if self.feature_names else range(len(importance)),
            'importance': importance
        }).sort_values('importance', ascending=False)
