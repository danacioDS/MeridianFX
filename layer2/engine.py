import pandas as pd
import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, timezone
from .data.provider import DataProvider
from .features.technical import TechnicalFeatures
from .models.xgboost_model import XGBoostModel
from .models.logistic_model import LogisticModel
from .explainers.shap_explainer import SHAPExplainer
from .decision.filter import EconomicFilter
from .config import MODEL_PATH
from .models.registry import ModelRegistry

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

class DecisionEngine:
    """Motor de decisión principal con caché persistente en disco."""
    
    def __init__(self):
        self.data_provider = DataProvider()
        self.economic_filter = EconomicFilter()
        self.registry = ModelRegistry()
        
        # Caché en memoria
        self.cache = {}
        self.cache_ttl = 300
        
        # Modelos por par
        self.xgb_models = {}
        self.logistic_models = {}
        self.shap_explainers = {}
        
        # Cargar caché desde disco
        self._load_cache()
    
    def _get_model_for_pair(self, pair: str, model_type: str = "xgboost"):
        """Obtiene el modelo específico para un par, cargándolo bajo demanda."""
        cache_key = f"{pair}_{model_type}"
        
        if cache_key in self.xgb_models:
            return self.xgb_models[cache_key]
        
        try:
            # Buscar modelo activo en el registry
            active = self.registry.get_active(pair, model_type)
            if active:
                model_path = active.get('path')
                if model_path and os.path.exists(model_path):
                    if model_type == "xgboost":
                        model = XGBoostModel(model_path)
                    else:
                        model = LogisticModel(model_path)
                    
                    self.xgb_models[cache_key] = model
                    print(f"✅ Modelo {model_type} cargado para {pair}")
                    return model
        except Exception as e:
            print(f"⚠️ Error cargando modelo {model_type} para {pair}: {e}")
        
        return None
    
    def _load_cache(self):
        """Carga caché desde disco."""
        cache_file = os.path.join(CACHE_DIR, "forecast_cache.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        self.cache[key] = {
                            'data': value['data'],
                            'timestamp': datetime.fromisoformat(value['timestamp'])
                        }
                    print(f"✅ Caché cargado desde disco ({len(self.cache)} entradas)")
            except Exception as e:
                print(f"⚠️ Error cargando caché: {e}")
    
    def _save_cache(self):
        """Guarda caché en disco."""
        cache_file = os.path.join(CACHE_DIR, "forecast_cache.json")
        try:
            data = {}
            for key, entry in self.cache.items():
                data[key] = {
                    'data': entry['data'],
                    'timestamp': entry['timestamp'].isoformat()
                }
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Error guardando caché: {e}")
    
    def _get_cached(self, key: str):
        """Obtiene del caché si no ha expirado."""
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() - entry['timestamp'] < timedelta(seconds=self.cache_ttl):
                return entry['data']
        return None
    
    def _set_cache(self, key: str, data):
        """Guarda en caché (memoria + disco)."""
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }
        self._save_cache()
    
    def get_forecast(self, pair: str) -> dict:
        """Obtiene forecast completo para un par específico."""
        cache_key = f"forecast_{pair}"
        
        cached = self._get_cached(cache_key)
        if cached:
            print(f"📦 Usando caché para {pair}")
            return cached
        
        print(f"📊 Generando forecast para {pair}...")
        
        try:
            # 1. Obtener datos
            result = self.data_provider.get_historical(pair, period="1y")
            df = result['data']
            
            # 2. Generar features
            df_feat = TechnicalFeatures.generate(df)
            feature_cols = TechnicalFeatures.get_feature_names()
            latest = df_feat.iloc[-1:][feature_cols].dropna()
            
            if latest.empty:
                print("⚠️ No hay datos suficientes")
                return self._fallback_forecast(pair)
            
            # 3. Cargar modelo específico para el par
            xgb_model = self._get_model_for_pair(pair, "xgboost")
            is_trained = xgb_model is not None and xgb_model.model is not None
            
            if is_trained:
                try:
                    xgb_pred = xgb_model.predict(latest)
                    probability = xgb_pred.get('probability', 0.5)
                    print(f"✅ XGBoost predijo para {pair}: {xgb_pred}")
                except Exception as e:
                    print(f"⚠️ XGBoost falló: {e}")
                    xgb_pred = self._heuristic_forecast(latest)
                    probability = xgb_pred.get('probability', 0.5)
            else:
                xgb_pred = self._heuristic_forecast(latest)
                probability = xgb_pred.get('probability', 0.5)
                print(f"⚠️ Usando heuristic para {pair}")
            
            # 4. SHAP explicación
            shap_explanation = None
            if is_trained and xgb_model is not None:
                try:
                    X_background = df_feat[feature_cols].dropna()
                    if len(X_background) > 0:
                        shap_explainer = SHAPExplainer(
                            xgb_model.model,
                            xgb_model.feature_names,
                            X_background
                        )
                        shap_explanation = shap_explainer.explain(latest)
                except Exception as e:
                    print(f"⚠️ SHAP falló: {e}")
            
            # 5. Economic filter
            filtered = self.economic_filter.apply(xgb_pred)
            
            # 6. Determinar dirección
            direction = "UP" if probability > 0.55 else "DOWN" if probability < 0.45 else "NEUTRAL"
            expected_return = (probability - 0.5) * 0.02
            
            response = {
                'direction': direction,
                'probability': probability,
                'expected_return': expected_return,
                'expected_volatility': 0.12,
                'actionable': filtered.get('actionable', False),
                'confidence': filtered.get('confidence', probability),
                'signal_strength': filtered.get('signal_strength', 'moderate'),
                'edge_ratio': filtered.get('edge_ratio', 0.0),
                'net_return': filtered.get('net_return', 0.0),
                'position_size': filtered.get('position_size', 0.0),
                'model': {
                    'version': 'xgb-v1.0' if is_trained else 'heuristic-v1.0',
                    'type': 'xgboost' if is_trained else 'heuristic'
                },
                'shap': shap_explanation,
                'data_provider': {
                    'source': result['provider'],
                    'fallback_used': result['fallback_used'],
                    'freshness': result['freshness'],
                    'last_price': result['last_price']
                },
                'timestamp': datetime.now().isoformat()
            }
            
            self._set_cache(cache_key, response)
            return response
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return self._fallback_forecast(pair)
    
    def _heuristic_forecast(self, latest: pd.DataFrame) -> dict:
        rsi = latest['rsi_14'].iloc[-1] if 'rsi_14' in latest else 50
        macd = latest['macd'].iloc[-1] if 'macd' in latest else 0
        
        if rsi > 70 and macd > 0:
            return {'direction': 'DOWN', 'probability': 0.65}
        elif rsi < 30 and macd < 0:
            return {'direction': 'UP', 'probability': 0.65}
        else:
            return {'direction': 'UP' if macd > 0 else 'DOWN', 'probability': 0.55}
    
    def _fallback_forecast(self, pair: str) -> dict:
        return {
            'direction': 'NEUTRAL',
            'probability': 0.5,
            'expected_return': 0.0,
            'expected_volatility': 0.0,
            'actionable': False,
            'confidence': 0.0,
            'signal_strength': 0.0,
            'edge_ratio': 0.0,
            'net_return': 0.0,
            'position_size': 0.0,
            'model': {'version': 'fallback', 'type': 'fallback'},
            'shap': None,
            'data_provider': {'source': 'none', 'fallback_used': True, 'freshness': 'UNKNOWN'},
            'timestamp': datetime.now().isoformat()
        }
