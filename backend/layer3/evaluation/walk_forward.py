"""
Walk-Forward Evaluation — Layer 3 v5.0 §7.1

Implementa walk-forward backtesting con:
- Entrenamiento por ventana (reentrenamiento)
- Target futuro t+h (no backward)
- Purging para evitar leakage
- Múltiples ventanas OOS
- Métricas estadísticas, económicas y robustez
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pytz
from sklearn.base import clone


class WalkForwardEvaluator:
    """
    Walk-forward backtesting con rolling windows.
    
    Cada ventana:
    1. Toma datos de entrenamiento (train_years)
    2. Aplica purging (horizon días antes del test)
    3. Entrena modelo clonado con hiperparámetros del original
    4. Evalúa en test OOS
    5. Calcula métricas
    """
    
    def __init__(self, data_provider=None):
        self.data_provider = data_provider
        self.results = {}
    
    def _get_data(self, pair: str, period: str = "5y") -> pd.DataFrame:
        """Obtiene datos históricos."""
        if self.data_provider:
            result = self.data_provider.get_historical(pair, period=period)
            return result['data']
        return pd.DataFrame()
    
    def _calculate_log_returns(self, df: pd.DataFrame) -> pd.Series:
        return np.log(df['Close'] / df['Close'].shift(1))
    
    def _calculate_forward_target(self, returns: pd.Series, horizon: int = 5) -> pd.Series:
        """
        Target futuro: 1 si el retorno acumulado de t+1 a t+horizon es > 0.

        El target mira estrictamente hacia adelante.
        Las últimas `horizon` observaciones no tienen target conocido
        y permanecen como NaN.
        """
        # Retorno acumulado estrictamente futuro:
        # t -> t+1, ..., t+horizon.
        future_returns = sum(
            returns.shift(-i) for i in range(1, horizon + 1)
        )

        # Preservar NaN cuando no existe suficiente información futura.
        target = pd.Series(np.nan, index=returns.index, dtype="float64")
        valid = future_returns.notna()
        target.loc[valid] = (future_returns.loc[valid] > 0).astype(int)

        return target

    def _calculate_metrics(
        self,
        y_true,
        y_pred,
        y_proba,
        future_returns,
        horizon: int = 5,
    ) -> Dict:
        """
        Calcula métricas predictivas y económicas de forma coherente
        con el horizonte del target.

        Predictivas:
        - DA
        - AUC
        - Brier
        - ECE

        Económicas:
        - Utiliza el mismo retorno futuro que define el target.
        - Las observaciones económicas se toman cada `horizon` pasos
          para evitar solapamiento entre períodos de holding.
        """
        from sklearn.metrics import (
            accuracy_score,
            roc_auc_score,
            brier_score_loss,
        )

        y_true = np.asarray(y_true)
        y_pred = np.asarray(y_pred)
        y_proba = np.asarray(y_proba)
        future_returns = np.asarray(future_returns, dtype=float)

        # ------------------------------------------------------------
        # MÉTRICAS PREDICTIVAS
        # ------------------------------------------------------------

        accuracy = accuracy_score(y_true, y_pred)

        auc = (
            roc_auc_score(y_true, y_proba)
            if len(np.unique(y_true)) > 1
            else 0.5
        )

        # NO invertir automáticamente una señal con AUC < 0.5.
        # El resultado OOS debe reflejar exactamente el modelo evaluado.

        brier = brier_score_loss(y_true, y_proba)

        # ECE simplificado
        n_bins = 10
        bin_edges = np.linspace(0, 1, n_bins + 1)
        ece = 0.0

        for i in range(n_bins):
            if i == n_bins - 1:
                mask = (
                    (y_proba >= bin_edges[i])
                    & (y_proba <= bin_edges[i + 1])
                )
            else:
                mask = (
                    (y_proba >= bin_edges[i])
                    & (y_proba < bin_edges[i + 1])
                )

            if np.sum(mask) > 0:
                avg_prob = np.mean(y_proba[mask])
                avg_actual = np.mean(y_true[mask])
                ece += (
                    abs(avg_prob - avg_actual)
                    * np.sum(mask)
                    / len(y_proba)
                )

        # ------------------------------------------------------------
        # MÉTRICAS ECONÓMICAS
        # ------------------------------------------------------------

        # Solo observaciones con retorno futuro completamente conocido.
        valid = np.isfinite(future_returns)

        future_returns = future_returns[valid]
        economic_pred = y_pred[valid]

        if len(future_returns) >= horizon:
            # Una posición 1 = long, 0 = short.
            positions = np.where(economic_pred == 1, 1.0, -1.0)

            # Tomar períodos no solapados para las métricas económicas.
            indices = np.arange(0, len(future_returns), horizon)

            period_returns = future_returns[indices]
            period_positions = positions[indices]

            # El target está definido mediante log-returns.
            # Por tanto, la estrategia también se evalúa en log-return.
            strategy_log_returns = (
                period_positions * period_returns
            )

            # Sharpe sobre períodos de holding de `horizon` días.
            mean_ret = np.mean(strategy_log_returns)
            std_ret = np.std(strategy_log_returns)

            sharpe = (
                mean_ret / (std_ret + 1e-6)
                * np.sqrt(252 / horizon)
            )

            # Equity curve correcta para log-returns.
            cumulative = np.exp(
                np.cumsum(strategy_log_returns)
            )

            running_max = np.maximum.accumulate(cumulative)

            max_drawdown = np.min(
                cumulative / running_max - 1
            )

            gains = strategy_log_returns[
                strategy_log_returns > 0
            ].sum()

            losses = abs(
                strategy_log_returns[
                    strategy_log_returns < 0
                ].sum()
            )

            profit_factor = (
                gains / losses
                if losses > 0
                else np.inf
            )

            net_return = cumulative[-1] - 1

        else:
            sharpe = 0.0
            max_drawdown = 0.0
            profit_factor = 0.0
            net_return = 0.0

        return {
            'DA': float(accuracy),
            'AUC': float(auc),
            'Brier': float(brier),
            'ECE': float(ece),
            'Sharpe': float(sharpe),
            'MaxDD': float(max_drawdown),
            'ProfitFactor': (
                float(profit_factor)
                if profit_factor != np.inf
                else float('inf')
            ),
            'NetReturn': float(net_return),
            'n_samples': int(len(y_true)),
            'economic_samples': int(
                len(future_returns) // horizon
                if len(future_returns) >= horizon
                else 0
            ),
        }

    def evaluate(self, pair: str, model, horizon: int = 5, 
                 train_years: int = 3, test_years: int = 1,
                 step_years: int = 1) -> Dict:
        """
        Walk-forward evaluation con rolling windows.
        """
        df = self._get_data(pair, period="5y")
        if df.empty:
            return {'error': 'No data available', 'windows': []}
        
        # Preparar features y target
        from layer2.features.technical import TechnicalFeatures
        
        df_feat = TechnicalFeatures.generate(df)
        returns = self._calculate_log_returns(df)
        target = self._calculate_forward_target(returns, horizon)
        
        feature_cols = TechnicalFeatures.get_feature_names()

        # Alinear features, target y retornos.
        X = df_feat[feature_cols].dropna()
        y = target.loc[X.index]
        returns_aligned = returns.loc[X.index]

        # El target futuro no existe para las últimas `horizon` observaciones.
        # Eliminar esas filas evita convertir NaN futuros en clase 0.
        valid_mask = y.notna()

        X = X.loc[valid_mask]
        y = y.loc[valid_mask].astype(int)
        returns_aligned = returns_aligned.loc[valid_mask]

        if len(X) < 500:
            return {'error': 'Insufficient data for walk-forward', 'windows': []}
        
        # Configuración de ventanas
        n = len(X)
        train_size = int(train_years * 252)
        test_size = int(test_years * 252)
        step_size = int(step_years * 252)
        purge_size = horizon  # Días de purging antes del test
        
        # Calcular número de ventanas
        if n - train_size - purge_size - test_size < 0:
            return {'error': 'Not enough data for even one window', 'windows': []}
        
        n_windows = (n - train_size - purge_size - test_size) // step_size + 1
        n_windows = max(1, min(n_windows, 10))  # Máximo 10 ventanas
        
        window_results = []
        rolling_sharpe = []
        oos_metrics = []
        
        for w in range(n_windows):
            train_end = w * step_size
            test_start = train_end + train_size + purge_size
            test_end = min(test_start + test_size, n)
            
            if test_end - test_start < 30 or test_start >= n:
                break
            
            X_train = X.iloc[train_end:train_end + train_size]
            y_train = y.iloc[train_end:train_end + train_size]
            
            X_test = X.iloc[test_start:test_end]
            y_test = y.iloc[test_start:test_end]
            returns_test = returns_aligned.iloc[test_start:test_end]
            
            # Clonar y entrenar modelo en esta ventana
            try:
                # Obtener el estimador base (XGBoost o logistic)
                base_estimator = model.model
                
                # Clonar para esta ventana
                wf_model = clone(base_estimator)
                
                # Entrenar con datos de esta ventana
                wf_model.fit(X_train, y_train)
                
                # Predecir en test
                y_proba = wf_model.predict_proba(X_test)[:, 1]
                y_pred = (y_proba >= 0.5).astype(int)
                
            except Exception as exc:
                # Si falla, no continuar con esta ventana
                print(f"⚠️ Window {w+1} failed: {exc}")
                continue
            
            # Calcular métricas
            metrics = self._calculate_metrics(
                y_test.values,
                y_pred,
                y_proba,
                future_returns_test.values,
                horizon=horizon,
            )
            
            window_results.append({
                'window': w + 1,
                'train_start': X.index[train_end],
                'train_end': X.index[train_end + train_size - 1],
                'test_start': X.index[test_start],
                'test_end': X.index[test_end - 1],
                'n_train': len(X_train),
                'n_test': len(X_test),
                'metrics': metrics
            })
            
            rolling_sharpe.append(metrics['Sharpe'])
            oos_metrics.append(metrics)
        
        if not window_results:
            return {'error': 'No windows completed successfully', 'windows': []}
        
        # Agregar resultados
        all_metrics = [w['metrics'] for w in window_results]
        
        # Calcular Profit Factor promedio (manejar infinitos)
        pf_values = [m['ProfitFactor'] for m in all_metrics if m['ProfitFactor'] != float('inf')]
        mean_pf = np.mean(pf_values) if pf_values else 0.0
        
        # Calcular Net Return promedio
        nr_values = [m['NetReturn'] for m in all_metrics]
        mean_nr = np.mean(nr_values) if nr_values else 0.0
        
        return {
            'pair': pair,
            'horizon': horizon,
            'n_windows': len(window_results),
            'windows': window_results,
            'aggregate': {
                'mean_DA': np.mean([m['DA'] for m in all_metrics]),
                'std_DA': np.std([m['DA'] for m in all_metrics]),
                'mean_AUC': np.mean([m['AUC'] for m in all_metrics]),
                'std_AUC': np.std([m['AUC'] for m in all_metrics]),
                'mean_ECE': np.mean([m['ECE'] for m in all_metrics]),
                'std_ECE': np.std([m['ECE'] for m in all_metrics]),
                'mean_Sharpe': np.mean([m['Sharpe'] for m in all_metrics]),
                'std_Sharpe': np.std([m['Sharpe'] for m in all_metrics]),
                'mean_MaxDD': np.mean([m['MaxDD'] for m in all_metrics]),
                'std_MaxDD': np.std([m['MaxDD'] for m in all_metrics]),
                'mean_ProfitFactor': float(mean_pf),
                'mean_NetReturn': float(mean_nr),
            },
            'rolling_sharpe': rolling_sharpe,
            'oos_metrics': oos_metrics,
            'total_test_samples': sum(w['n_test'] for w in window_results),
            'timestamp': datetime.now(pytz.UTC).isoformat()
        }

    def evaluate_expanding(self, pair: str, model, horizon: int = 5,
                           initial_train_years: int = 3, test_years: int = 1,
                           step_years: int = 1) -> Dict:
        """
        Walk-forward con expanding window.
        
        Window 1: Train: 0 → T1, Test: T1 → T2
        Window 2: Train: 0 → T2, Test: T2 → T3
        Window 3: Train: 0 → T3, Test: T3 → T4
        """
        df = self._get_data(pair, period="7y")
        if df.empty:
            return {'error': 'No data available', 'windows': []}
        
        from layer2.features.technical import TechnicalFeatures
        
        df_feat = TechnicalFeatures.generate(df)
        returns = self._calculate_log_returns(df)
        target = self._calculate_forward_target(returns, horizon)
        
        feature_cols = TechnicalFeatures.get_feature_names()

        # Alinear features, target y retornos.
        X = df_feat[feature_cols].dropna()
        y = target.loc[X.index]
        returns_aligned = returns.loc[X.index]

        # El target futuro no existe para las últimas `horizon` observaciones.
        # Eliminar esas filas evita convertir NaN futuros en clase 0.
        valid_mask = y.notna()

        X = X.loc[valid_mask]
        y = y.loc[valid_mask].astype(int)
        returns_aligned = returns_aligned.loc[valid_mask]

        if len(X) < 500:
            return {'error': 'Insufficient data', 'windows': []}
        
        n = len(X)
        initial_train = int(initial_train_years * 252)
        test_size = int(test_years * 252)
        step_size = int(step_years * 252)
        purge_size = horizon
        
        # Calcular ventanas
        n_windows = (n - initial_train - purge_size - test_size) // step_size + 1
        n_windows = max(1, min(n_windows, 8))
        
        window_results = []
        rolling_sharpe = []
        
        for w in range(n_windows):
            train_end = initial_train + w * step_size
            test_start = train_end + purge_size
            test_end = min(test_start + test_size, n)
            
            if test_end - test_start < 30:
                break
            
            X_train = X.iloc[:train_end]
            y_train = y.iloc[:train_end]
            X_test = X.iloc[test_start:test_end]
            y_test = y.iloc[test_start:test_end]
            returns_test = returns_aligned.iloc[test_start:test_end]

            # Retorno futuro del mismo horizonte utilizado por el target.
            # t -> t+1 ... t+horizon.
            future_returns_test = sum(
                returns_aligned.shift(-i).iloc[test_start:test_end]
                for i in range(1, horizon + 1)
            )

            # Entrenar modelo en esta ventana
            try:
                base_estimator = model.model
                from sklearn.base import clone
                wf_model = clone(base_estimator)
                wf_model.fit(X_train, y_train)
                
                y_proba = wf_model.predict_proba(X_test)[:, 1]
                y_pred = (y_proba >= 0.5).astype(int)
            except Exception as exc:
                print(f"⚠️ Window {w+1} failed: {exc}")
                continue
            
            metrics = self._calculate_metrics(
                y_test.values,
                y_pred,
                y_proba,
                future_returns_test.values,
                horizon=horizon,
            )
            
            window_results.append({
                'window': w + 1,
                'train_size': len(X_train),
                'test_size': len(X_test),
                'test_start': X.index[test_start],
                'test_end': X.index[test_end - 1],
                'metrics': metrics,
                'future_returns': future_returns_test.values.tolist(),
                'y_pred': y_pred.tolist(),
                'y_true': y_test.values.tolist()
            })
            
            rolling_sharpe.append(metrics['Sharpe'])
        
        if not window_results:
            return {'error': 'No windows completed', 'windows': []}
        
        all_metrics = [w['metrics'] for w in window_results]
        
        return {
            'pair': pair,
            'horizon': horizon,
            'n_windows': len(window_results),
            'windows': window_results,
            'aggregate': {
                'mean_DA': np.mean([m['DA'] for m in all_metrics]),
                'std_DA': np.std([m['DA'] for m in all_metrics]),
                'mean_AUC': np.mean([m['AUC'] for m in all_metrics]),
                'std_AUC': np.std([m['AUC'] for m in all_metrics]),
                'mean_ECE': np.mean([m['ECE'] for m in all_metrics]),
                'mean_Sharpe': np.mean([m['Sharpe'] for m in all_metrics]),
                'std_Sharpe': np.std([m['Sharpe'] for m in all_metrics]),
                'mean_MaxDD': np.mean([m['MaxDD'] for m in all_metrics]),
                'mean_ProfitFactor': np.mean([m['ProfitFactor'] for m in all_metrics if m['ProfitFactor'] != float('inf')]),
                'mean_NetReturn': np.mean([m['NetReturn'] for m in all_metrics]),
            },
            'rolling_sharpe': rolling_sharpe,
            'total_test_samples': sum(w['test_size'] for w in window_results),
            'timestamp': datetime.now(pytz.UTC).isoformat()
        }
