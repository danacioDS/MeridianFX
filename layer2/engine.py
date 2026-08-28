import pandas as pd
from datetime import datetime, timedelta
from .data.provider import DataProvider
from .features.technical import TechnicalFeatures
from .models.xgboost_model import XGBoostModel
from .models.logistic_model import LogisticModel
from .models.registry import ModelRegistry
from .explainers.shap_explainer import SHAPExplainer
from .decision.filter import EconomicFilter
from .config import MODEL_PATH

class DecisionEngine:
    """Motor de decisión principal con caché."""
    
    def __init__(self):
        self.data_provider = DataProvider()
        self.xgb_model = None
        self.logistic_model = None
        self.shap_explainer = None
        self.registry = ModelRegistry()
        self.economic_filter = EconomicFilter()
        self.is_trained = False
        
        # Caché simple
        self.cache = {}
        self.cache_ttl = 300  # 5 minutos
        
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
    
    def _get_cached(self, key: str):
        """Obtiene del caché si no ha expirado."""
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() - entry['timestamp'] < timedelta(seconds=self.cache_ttl):
                return entry['data']
        return None
    
    def _set_cache(self, key: str, data):
        """Guarda en caché."""
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    def train(self, pair: str = "USD/JPY", period: str = "2y"):
        """Entrena ambos modelos y registra el mejor."""
        print(f"🔄 Entrenando modelos para {pair}...")
        
        result = self.data_provider.get_historical(pair, period=period)
        df = result['data']
        print(f"📊 Datos obtenidos: {len(df)} filas (provider: {result['provider']})")
        
        df_feat = TechnicalFeatures.generate(df)
        print(f"📈 Features generadas: {len(df_feat)} filas")
        
        if len(df_feat) == 0:
            raise ValueError("No se pudieron generar features")
        
        y = TechnicalFeatures.create_target(df_feat)
        feature_cols = TechnicalFeatures.get_feature_names()
        X = df_feat[feature_cols].dropna()
        y = y[X.index]
        
        print(f"🎯 Muestras: {X.shape[0]}, Features: {X.shape[1]}")
        
        if len(X) < 50:
            raise ValueError(f"Datos insuficientes: {len(X)} muestras")
        
        print("\n📊 Entrenando XGBoost...")
        xgb = XGBoostModel()
        xgb_metrics = xgb.train(X, y)
        
        print("\n📊 Entrenando Logistic Regression...")
        log = LogisticModel()
        log_metrics = log.train(X, y)
        
        xgb_version = "v1.0"
        log_version = "v1.0"
        
        xgb_path = f"models/xgboost_{pair.replace('/', '_')}_{xgb_version}.pkl"
        log_path = f"models/logistic_{pair.replace('/', '_')}_{log_version}.pkl"
        
        xgb.save(xgb_path)
        log.save(log_path)
        
        xgb_id = self.registry.register(pair, 'xgboost', xgb_version, xgb_metrics, xgb_path)
        log_id = self.registry.register(pair, 'logistic', log_version, log_metrics, log_path)
        
        print(f"\n✅ Modelos registrados:")
        print(f"   XGBoost: {xgb_id} (AUC: {xgb_metrics['auc']:.4f})")
        print(f"   Logistic: {log_id} (AUC: {log_metrics['auc']:.4f})")
        
        active_xgb = self.registry.get_active(pair, 'xgboost')
        if active_xgb:
            self.xgb_model = XGBoostModel(active_xgb['path'])
            self.is_trained = True
            
            try:
                X_background = X.sample(min(100, len(X)))
                self.shap_explainer = SHAPExplainer(
                    self.xgb_model.model,
                    self.xgb_model.feature_names,
                    X_background
                )
                print("✅ SHAP Explainer inicializado")
            except Exception as e:
                print(f"⚠️ SHAP no inicializado: {e}")
        
        return {'xgb': xgb_metrics, 'logistic': log_metrics}
    
    def get_forecast(self, pair: str) -> dict:
        """Obtiene forecast completo con caché."""
        cache_key = f"forecast_{pair}"
        
        # Intentar caché
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
            
            # Guardar en caché
            self._set_cache(cache_key, response)
            return response
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return self._fallback_forecast(pair)
    
    def get_drivers(self, pair: str) -> dict:
        """Obtiene drivers (SHAP) con caché."""
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
