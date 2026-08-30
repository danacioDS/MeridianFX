"""
Ensemble Model — Layer 3 v5.0 §4.5

Combines XGBoost + Elastic Net + ARIMA predictions.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Any


class EnsembleModel:
    """
    Ensemble of XGBoost, Elastic Net, and ARIMA.
    §4.5: All models produce P(direction = up)
    """
    
    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or {
            'xgboost': 0.5,
            'elastic_net': 0.3,
            'arima': 0.2
        }
        self.models = {}
        self.fitted = False
    
    def add_model(self, name: str, model, weight: float = None):
        """Add a model to the ensemble."""
        self.models[name] = model
        if weight is not None:
            self.weights[name] = weight
    
    def fit(self, X, y) -> None:
        """Fit all models in the ensemble."""
        for name, model in self.models.items():
            if hasattr(model, 'fit'):
                try:
                    model.fit(X, y)
                except Exception as e:
                    print(f"Model {name} fit error: {e}")
        self.fitted = True
    
    def predict(self, X: pd.DataFrame) -> Dict:
        """
        Generate ensemble prediction.
        §4.5: Ensemble = weighted average of individual predictions
        """
        if not self.fitted or not self.models:
            return {
                'direction': 'NEUTRAL',
                'probability': 0.5,
                'expected_return': 0.0,
                'expected_volatility': 0.0
            }
        
        predictions = []
        total_weight = 0
        
        for name, model in self.models.items():
            try:
                if hasattr(model, 'predict'):
                    pred = model.predict(X)
                    if isinstance(pred, dict):
                        prob = pred.get('probability', 0.5)
                        weight = self.weights.get(name, 1.0 / len(self.models))
                        predictions.append({
                            'name': name,
                            'probability': prob,
                            'weight': weight,
                            'prediction': pred
                        })
                        total_weight += weight
            except Exception as e:
                print(f"Model {name} predict error: {e}")
        
        if not predictions:
            return {
                'direction': 'NEUTRAL',
                'probability': 0.5,
                'expected_return': 0.0,
                'expected_volatility': 0.0
            }
        
        # Weighted average of probabilities
        weighted_prob = sum(p['probability'] * p['weight'] / total_weight 
                           for p in predictions)
        
        # Weighted average of expected returns
        weighted_return = sum(
            p['prediction'].get('expected_return', 0) * p['weight'] / total_weight
            for p in predictions
        )
        
        # Weighted average of volatility
        weighted_vol = sum(
            p['prediction'].get('expected_volatility', 0.1) * p['weight'] / total_weight
            for p in predictions
        )
        
        # Determine direction
        if weighted_prob > 0.6:
            direction = 'BULLISH'
        elif weighted_prob < 0.4:
            direction = 'BEARISH'
        else:
            direction = 'NEUTRAL'
        
        return {
            'direction': direction,
            'probability': weighted_prob,
            'expected_return': weighted_return,
            'expected_volatility': weighted_vol,
            'ensemble_details': {
                'models': predictions,
                'weights': self.weights
            }
        }
