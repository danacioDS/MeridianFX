"""
Evaluación sistemática de todos los pares y horizontes.
Aplica el mismo protocolo de validación purgada a cada combinación.
"""

from backend.layer2.data.provider import DataProvider
from backend.layer2.features.technical import TechnicalFeatures

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, brier_score_loss

import numpy as np
import pandas as pd
from datetime import datetime

# Configuración
PAIRS = [
    'USD/JPY', 'EUR/USD', 'GBP/USD',
    'USD/CNY', 'USD/MXN', 'USD/BRL',
    'USD/ARS', 'USD/BOB', 'USD/CHF'
]

HORIZONS = [5, 10, 20, 30]
N_FOLDS = 5

dp = DataProvider()
results = []

print("\n" + "="*80)
print("MERIDIANFX — SYSTEMATIC PAIR EVALUATION")
print("="*80)
print(f"Pairs: {len(PAIRS)}")
print(f"Horizons: {HORIZONS}")
print(f"Folds: {N_FOLDS}")
print(f"Model: Logistic Regression")
print("="*80)

for pair in PAIRS:
    for h in HORIZONS:
        print(f"\n📊 {pair} — {h}d")
        
        try:
            # Obtener datos
            result = dp.get_historical(pair, period="2y")
            df = result["data"]
            df_feat = TechnicalFeatures.generate(df)
            feature_cols = TechnicalFeatures.get_feature_names()
            
            y = TechnicalFeatures.create_target(df_feat, forward_days=h)
            X = df_feat[feature_cols]
            
            valid = X.notna().all(axis=1) & y.notna()
            X = X.loc[valid]
            y = y.loc[valid].astype(int)
            
            n = len(X)
            
            if n < 100:
                print(f"  ⚠️ Datos insuficientes: {n} observaciones")
                continue
            
            test_size = n // (N_FOLDS + 1)
            fold_results = []
            
            for i in range(1, N_FOLDS + 1):
                train_end = test_size * i
                test_start = train_end + h
                test_end = test_start + test_size
                
                if test_end > n:
                    break
                
                X_train = X.iloc[:train_end]
                y_train = y.iloc[:train_end]
                X_test = X.iloc[test_start:test_end]
                y_test = y.iloc[test_start:test_end]
                
                if y_train.nunique() < 2 or y_test.nunique() < 2:
                    continue
                
                model = Pipeline([
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                    ("logistic", LogisticRegression(max_iter=5000, random_state=42))
                ])
                
                model.fit(X_train, y_train)
                proba = model.predict_proba(X_test)[:, 1]
                
                auc = roc_auc_score(y_test, proba)
                brier = brier_score_loss(y_test, proba)
                
                fold_results.append({
                    'auc': auc,
                    'brier': brier,
                    'n_test': len(y_test),
                    'n_up': int(y_test.sum())
                })
            
            if fold_results:
                aucs = [r['auc'] for r in fold_results]
                briers = [r['brier'] for r in fold_results]
                n_ups = [r['n_up'] for r in fold_results]
                
                mean_auc = np.mean(aucs)
                std_auc = np.std(aucs)
                mean_brier = np.mean(briers)
                
                status = "✅" if mean_auc > 0.55 and std_auc < 0.15 else "⚠️" if mean_auc > 0.50 else "❌"
                
                results.append({
                    'pair': pair,
                    'horizon': h,
                    'mean_auc': mean_auc,
                    'std_auc': std_auc,
                    'min_auc': min(aucs),
                    'max_auc': max(aucs),
                    'mean_brier': mean_brier,
                    'n_folds': len(fold_results),
                    'avg_up': np.mean(n_ups),
                    'status': status
                })
                
                print(f"  AUC: {mean_auc:.4f} ± {std_auc:.4f}  |  "
                      f"Min: {min(aucs):.4f}  |  Max: {max(aucs):.4f}  |  "
                      f"Folds: {len(fold_results)}  |  {status}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")

# Resumen final
print("\n" + "="*80)
print("RESUMEN FINAL")
print("="*80)

df_results = pd.DataFrame(results)
df_results = df_results.sort_values(['status', 'mean_auc'], ascending=[False, False])

print("\n" + df_results.to_string(index=False))

# Mejores combinaciones
print("\n" + "="*80)
print("MEJORES COMBINACIONES (AUC > 0.55 y std < 0.15)")
print("="*80)

best = df_results[(df_results['mean_auc'] > 0.55) & (df_results['std_auc'] < 0.15)]
if not best.empty:
    print(best[['pair', 'horizon', 'mean_auc', 'std_auc', 'status']].to_string(index=False))
else:
    print("No se encontraron combinaciones estables con AUC > 0.55")

print("\n" + "="*80)
print(f"Evaluación completada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)
