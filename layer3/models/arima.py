"""
ARIMA Model — Layer 3 v5.0 §4.1

Time-series model for FX forecasting.
"""
import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA as StatsmodelsARIMA
from statsmodels.tsa.stattools import adfuller
from typing import Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class ARIMAModel:
    """ARIMA model for FX return forecasting."""
    
    def __init__(self, order: Tuple[int, int, int] = None):
        self.order = order
        self.model = None
        self.fitted = False
        self.feature_names = ['lag_1', 'lag_2', 'lag_3']
    
    def _adf_test(self, series: pd.Series) -> int:
        """
        ADF Test for stationarity (DIAGNOSTIC, not mechanical)
        §4.1: ADF as a diagnostic, not a mechanical step
        """
        try:
            result = adfuller(series.dropna())
            p_value = result[1]
            # Log-return is normally stationary → d = 0
            if p_value < 0.05:
                return 0
            else:
                # Non-stationary → d = 1
                return 1
        except:
            return 0
    
    def _search_order(self, series: pd.Series, max_p: int = 3, max_q: int = 3) -> Tuple[int, int, int]:
        """
        Search (p, q) space using AIC
        §4.1: p ∈ {0, 1, 2, 3}, q ∈ {0, 1, 2, 3}
        """
        best_aic = np.inf
        best_order = (1, 0, 1)
        d = 0  # Log-return is normally stationary
        
        for p in range(max_p + 1):
            for q in range(max_q + 1):
                try:
                    model = StatsmodelsARIMA(series, order=(p, d, q))
                    fitted = model.fit()
                    if fitted.aic < best_aic:
                        best_aic = fitted.aic
                        best_order = (p, d, q)
                except:
                    continue
        
        return best_order
    
    def fit(self, y: pd.Series) -> None:
        """Fit ARIMA model to target series."""
        # Step 1: ADF Test (diagnostic)
        d = self._adf_test(y)
        
        # Step 2: Search (p, q) space
        if self.order is None:
            self.order = self._search_order(y)
        else:
            d = self.order[1]
        
        # Step 3: Fit final model
        try:
            self.model = StatsmodelsARIMA(y, order=self.order)
            self.fitted_model = self.model.fit()
            self.fitted = True
        except Exception as e:
            print(f"ARIMA fit error: {e}")
            self.fitted = False
    
    def predict(self, X: pd.DataFrame = None) -> Dict:
        """
        Generate prediction with confidence interval.
        §4.1: Outputs expected_return, forecast_interval, probability_up
        """
        if not self.fitted or self.fitted_model is None:
            return {
                'direction': 'NEUTRAL',
                'probability': 0.5,
                'expected_return': 0.0,
                'expected_volatility': 0.0,
                'prediction_interval': {'lower': 0.0, 'upper': 0.0}
            }
        
        try:
            # Forecast 1 step ahead
            forecast_result = self.fitted_model.get_forecast(steps=1)
            forecast_mean = forecast_result.predicted_mean.iloc[0]
            forecast_se = forecast_result.se_mean.iloc[0]
            
            # Confidence interval (95%)
            lower = forecast_mean - 1.96 * forecast_se
            upper = forecast_mean + 1.96 * forecast_se
            
            # Probability of positive return (via CDF of normal)
            from scipy.stats import norm
            probability_up = norm.cdf(forecast_mean / forecast_se) if forecast_se > 0 else 0.5
            
            # Determine direction
            if probability_up > 0.6:
                direction = 'BULLISH'
            elif probability_up < 0.4:
                direction = 'BEARISH'
            else:
                direction = 'NEUTRAL'
            
            return {
                'direction': direction,
                'probability': probability_up,
                'expected_return': float(forecast_mean),
                'expected_volatility': float(forecast_se),
                'prediction_interval': {
                    'lower': float(lower),
                    'upper': float(upper)
                }
            }
        except Exception as e:
            print(f"ARIMA predict error: {e}")
            return {
                'direction': 'NEUTRAL',
                'probability': 0.5,
                'expected_return': 0.0,
                'expected_volatility': 0.0,
                'prediction_interval': {'lower': 0.0, 'upper': 0.0}
            }
