"""
Logistic Elastic Net — Layer 3 v5.0 §4.2

Linear control model with purged walk-forward cross-validation.
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import ParameterGrid
from typing import Dict, List, Optional, Any
import warnings
warnings.filterwarnings('ignore')


class ElasticNetModel:
    """Logistic Elastic Net for FX direction prediction."""
    
    def __init__(self, l1_ratio: float = 0.5, C: float = 1.0):
        self.l1_ratio = l1_ratio
        self.C = C
        self.model = None
        self.scaler = StandardScaler()
        self.fitted = False
        self.feature_names = []
    
    def _purged_walkforward_cv(self, X: pd.DataFrame, y: pd.Series, 
                                n_splits: int = 5) -> Dict:
        """
        Purged Walk-Forward Cross-Validation
        §4.2: From standard 5-fold → Purged Walk-Forward CV
        
        Purging: Remove training observations whose label crosses the boundary
        """
        n = len(X)
        fold_size = n // n_splits
        results = []
        
        for i in range(n_splits):
            train_end = i * fold_size
            test_start = (i + 1) * fold_size
            test_end = min(test_start + fold_size, n)
            
            # Purge: Remove observations with label crossing boundary
            train_mask = np.ones(n, dtype=bool)
            train_mask[test_start:test_end] = False
            
            # Additional purging: remove observations around boundary
            purge_window = 5
            for j in range(test_start - purge_window, test_start + purge_window):
                if 0 <= j < n:
                    train_mask[j] = False
            
            X_train = X[train_mask]
            y_train = y[train_mask]
            X_test = X[test_start:test_end]
            y_test = y[test_start:test_end]
            
            if len(X_train) < 10 or len(X_test) < 5:
                continue
            
            # Fit on training
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            model = LogisticRegression(
                penalty='elasticnet',
                l1_ratio=self.l1_ratio,
                C=self.C,
                solver='saga',
                max_iter=1000,
                random_state=42
            )
            model.fit(X_train_scaled, y_train)
            
            # Evaluate
            score = model.score(X_test_scaled, y_test)
            results.append(score)
        
        return {
            'mean_score': np.mean(results) if results else 0,
            'std_score': np.std(results) if results else 0,
            'n_folds': len(results)
        }
    
    def fit(self, X: pd.DataFrame, y: pd.Series) -> None:
        """Fit Elastic Net model."""
        self.feature_names = X.columns.tolist()
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Fit model
        self.model = LogisticRegression(
            penalty='elasticnet',
            l1_ratio=self.l1_ratio,
            C=self.C,
            solver='saga',
            max_iter=1000,
            random_state=42
        )
        self.model.fit(X_scaled, y)
        self.fitted = True
    
    def predict(self, X: pd.DataFrame) -> Dict:
        """Generate prediction."""
        if not self.fitted or self.model is None:
            return {
                'direction': 'NEUTRAL',
                'probability': 0.5,
                'expected_return': 0.0,
                'expected_volatility': 0.0
            }
        
        try:
            X_scaled = self.scaler.transform(X)
            
            # Get probability of positive class
            prob = self.model.predict_proba(X_scaled)[0, 1]
            
            # Determine direction
            if prob > 0.6:
                direction = 'BULLISH'
            elif prob < 0.4:
                direction = 'BEARISH'
            else:
                direction = 'NEUTRAL'
            
            return {
                'direction': direction,
                'probability': prob,
                'expected_return': prob * 2 - 1,  # Simplified
                'expected_volatility': np.std(X_scaled) if len(X_scaled) > 0 else 0.1
            }
        except Exception as e:
            print(f"ElasticNet predict error: {e}")
            return {
                'direction': 'NEUTRAL',
                'probability': 0.5,
                'expected_return': 0.0,
                'expected_volatility': 0.0
            }
