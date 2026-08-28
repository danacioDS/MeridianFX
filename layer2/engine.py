import pandas as pd
import json
import os
from datetime import datetime, timedelta
from .data.provider import DataProvider
from .features.technical import TechnicalFeatures
from .models.xgboost_model import XGBoostModel
from .models.logistic_model import LogisticModel
from .models.registry import ModelRegistry
from .explainers.shap_explainer import SHAPExplainer
from .decision.filter import EconomicFilter
from .config import MODEL_PATH

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

class DecisionEngine:
    """Motor de decisión principal con caché persistente en disco."""
    
    def __init__(self):
        self.data_provider = DataProvider()
        self.xgb_model = None
        self.logistic_model = None
        self.shap_explainer = None
        self.registry = ModelRegistry()
        self.economic_filter = EconomicFilter()
        self.is_trained = False
        
        # Caché en memoria
        self.cache = {}
        self.cache_ttl = 300  # 5 minutos
        
        # Cargar caché desde disco
        self._load_cache()
        
        # Cargar modelos activos
        active_xgb = self.registry.get_active('USD/JPY', 'xgboost')
        if active_xgb:
            self.xgb_model = XGBoostModel(active_xgb['path'])
            if self.xgb_model.model is not None:
                self.is_trained = True
                print(f"✅ XGBoost cargado: {active_xgb['version']}")
                
                try:
                    result = self.data_provider.get_historical('USD/JPY', period='1y')
                    df = result['data']
                    df_feat = TechnicalFeatures.generate(df)
                    feature_cols = TechnicalFeatures.get_feature_names()
                    X_background = df_feat[feature_cols].dropna()
                    
                    if len(X_background) > 0:
                        self.shap_explainer = SHAPExplainer(
                            self.xgb_model.model,
                            self.xgb_model.feature_names,
                            X_background
                        )
                        print("✅ SHAP Explainer inicializado")
                except Exception as e:
                    print(f"⚠️ SHAP no inicializado: {e}")
        
        active_log = self.registry.get_active('USD/JPY', 'logistic')
        if active_log:
            self.logistic_model = LogisticModel(active_log['path'])
            if self.logistic_model.model is not None:
                print(f"✅ Logistic cargado: {active_log['version']}")
        
        # Pre-cargar forecast en caché
        print("🔄 Pre-cargando forecast en caché...")
        self.get_forecast('USD/JPY')
        print("✅ Caché pre-cargado")
    
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
        """Obtiene forecast completo con caché persistente."""
        cache_key = f"forecast_{pair}"
        
        cached = self._get_cached(cache_key)
        if cached:
            print(f"📦 Usando caché para {pair}")
            return cached
        
        print(f"📊 Generando forecast para {pair}...")
        
        try:
            result = self.data_provider.get_historical(pair, period="1y")
            df = result['data']
            
            df_feat = TechnicalFeatures.generate(df)
            feature_cols = TechnicalFeatures.get_feature_names()
            latest = df_feat.iloc[-1:][feature_cols].dropna()
            
            if latest.empty:
                print("⚠️ No hay datos suficientes, usando fallback")
                return self._fallback_forecast(pair)
            
            if self.is_trained and self.xgb_model:
                try:
                    xgb_pred = self.xgb_model.predict(latest)
                except:
                    xgb_pred = self._heuristic_forecast(latest)
            else:
                xgb_pred = self._heuristic_forecast(latest)
            
            shap_explanation = None
            if self.shap_explainer is not None:
                try:
                    shap_explanation = self.shap_explainer.explain(latest)
                except Exception as e:
                    print(f"⚠️ SHAP falló: {e}")
            
            filtered = self.economic_filter.apply(xgb_pred)
            
            response = {
                'direction': filtered.get('direction'),
                'probability': filtered.get('probability'),
                'expected_return': filtered.get('expected_return'),
                'expected_volatility': filtered.get('expected_volatility'),
                'actionable': filtered.get('actionable'),
                'confidence': filtered.get('confidence'),
                'signal_strength': filtered.get('signal_strength'),
                'edge_ratio': filtered.get('edge_ratio'),
                'net_return': filtered.get('net_return'),
                'position_size': filtered.get('position_size'),
                'model': {
                    'version': 'xgb-v1.0' if self.is_trained else 'heuristic-v1.0',
                    'type': 'xgboost' if self.is_trained else 'heuristic'
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
    
    def get_drivers(self, pair: str) -> dict:
        """Obtiene drivers (SHAP) con caché persistente."""
        cache_key = f"drivers_{pair}"
        
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        try:
            forecast = self.get_forecast(pair)
            shap_data = forecast.get('shap', {})
            
            if not shap_data or 'contributions' not in shap_data:
                response = {
                    'pair': pair,
                    'shap': [],
                    'narrative': 'No SHAP explanation available',
                    'timestamp': datetime.now().isoformat()
                }
                self._set_cache(cache_key, response)
                return response
            
            contributions = shap_data['contributions']
            
            if not contributions:
                response = {
                    'pair': pair,
                    'shap': [],
                    'narrative': 'No SHAP explanation available',
                    'timestamp': datetime.now().isoformat()
                }
                self._set_cache(cache_key, response)
                return response
            
            top_drivers = contributions[:3]
            narrative_parts = []
            for d in top_drivers:
                direction = "positive" if d['contribution'] > 0 else "negative"
                narrative_parts.append(f"{d['feature']} ({direction}, {abs(d['contribution']):.3f})")
            
            narrative = f"Top drivers: " + ", ".join(narrative_parts)
            
            response = {
                'pair': pair,
                'shap': contributions,
                'narrative': narrative,
                'timestamp': datetime.now().isoformat()
            }
            
            self._set_cache(cache_key, response)
            return response
            
        except Exception as e:
            print(f"⚠️ get_drivers error: {e}")
            return {
                'pair': pair,
                'shap': [],
                'narrative': f'Error generating SHAP: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
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
            'direction': 'UP',
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
