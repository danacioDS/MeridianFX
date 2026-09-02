"""
Benchmarks — Estrategias de referencia para comparación.

Compara la estrategia del modelo con:
1. Always Long
2. Always Short
3. Buy-and-Hold del horizonte
4. Random 50/50
"""
import numpy as np
from typing import Dict, List, Any


class BenchmarkEvaluator:
    """
    Evalúa estrategias de referencia.
    """
    
    @staticmethod
    def always_long(future_returns: np.ndarray) -> np.ndarray:
        """Siempre mantener posición LONG."""
        return np.ones_like(future_returns)
    
    @staticmethod
    def always_short(future_returns: np.ndarray) -> np.ndarray:
        """Siempre mantener posición SHORT."""
        return -np.ones_like(future_returns)
    
    @staticmethod
    def buy_and_hold(future_returns: np.ndarray) -> np.ndarray:
        """Buy-and-hold del horizonte."""
        return np.ones_like(future_returns)
    
    @staticmethod
    def random_50_50(future_returns: np.ndarray, seed: int = 42) -> np.ndarray:
        """Posiciones aleatorias 50/50."""
        np.random.seed(seed)
        return np.random.choice([-1, 1], size=len(future_returns))
    
    @staticmethod
    def evaluate_strategy(strategy_returns: np.ndarray, horizon: int = 5) -> Dict:
        """
        Evalúa una estrategia con las mismas métricas que el modelo.
        """
        # Tomar períodos no solapados
        indices = np.arange(0, len(strategy_returns), horizon)
        period_returns = strategy_returns[indices]
        
        # Log-returns
        mean_ret = np.mean(period_returns)
        std_ret = np.std(period_returns)
        
        sharpe = mean_ret / (std_ret + 1e-6) * np.sqrt(252 / horizon)
        
        cumulative = np.exp(np.cumsum(period_returns))
        running_max = np.maximum.accumulate(cumulative)
        max_drawdown = np.min(cumulative / running_max - 1)
        
        gains = period_returns[period_returns > 0].sum()
        losses = abs(period_returns[period_returns < 0].sum())
        profit_factor = gains / losses if losses > 0 else np.inf
        net_return = cumulative[-1] - 1
        
        return {
            'Sharpe': float(sharpe),
            'MaxDD': float(max_drawdown),
            'ProfitFactor': float(profit_factor) if profit_factor != np.inf else float('inf'),
            'NetReturn': float(net_return),
            'n_periods': len(period_returns)
        }
    
    def compare(self, model_returns: np.ndarray, future_returns: np.ndarray, 
                horizon: int = 5) -> Dict[str, Any]:
        """
        Compara la estrategia del modelo contra benchmarks.
        """
        # Asegurar que tienen la misma longitud
        min_len = min(len(model_returns), len(future_returns))
        model_returns = model_returns[:min_len]
        future_returns = future_returns[:min_len]
        
        strategies = {
            'Model': model_returns,
            'Always Long': self.always_long(future_returns) * future_returns,
            'Always Short': self.always_short(future_returns) * future_returns,
            'Buy & Hold': self.buy_and_hold(future_returns) * future_returns,
            'Random 50/50': self.random_50_50(future_returns) * future_returns,
        }
        
        results = {}
        for name, returns in strategies.items():
            results[name] = self.evaluate_strategy(returns, horizon)
        
        return results
