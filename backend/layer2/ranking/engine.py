"""
Ranking Engine - Genera ranking de oportunidades con trazabilidad completa.
"""
import time
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from ..data.provider import DataProvider
from ..features.technical import TechnicalFeatures
from ..models.registry import ModelRegistry
from ..models.xgboost_model import XGBoostModel
from ..decision.filter import EconomicFilter

class RankingEngine:
    def __init__(self):
        self.data_provider = DataProvider()
        self.registry = ModelRegistry()
        self.economic_filter = EconomicFilter()
        
        # Todos los pares con modelo entrenado
        self.pairs = ['USD/JPY', 'EUR/USD', 'GBP/USD', 'USD/CNY', 'USD/MXN', 
                     'USD/BRL', 'USD/ARS', 'USD/BOB', 'USD/CHF']
        
        # Verificar modelos activos
        self.active_pairs = []
        for pair in self.pairs:
            active = self.registry.get_active(pair, 'xgboost')
            if active:
                self.active_pairs.append(pair)
                print(f"✅ {pair}: modelo activo")
            else:
                print(f"⚠️ {pair}: sin modelo")
        
        # Caché de ranking (v2.6)
        self._cache: Optional[Dict] = None
        self._cache_time: float = 0
        self._cache_ttl: int = 60  # segundos
    
    def get_ranking(self) -> Dict:
        # ─── Caché (v2.6) ───
        now = time.time()
        if self._cache and (now - self._cache_time) < self._cache_ttl:
            return self._cache
        
        # ─── Cálculo ───
        opportunities = []
        for pair in self.active_pairs:
            result = self._get_prediction(pair)
            if result:
                opportunities.append(result)
        
        opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
        for i, opp in enumerate(opportunities):
            opp['rank'] = i + 1
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'opportunities': opportunities,
            'top_opportunity': opportunities[0] if opportunities else None,
            'total_actionable': sum(1 for o in opportunities if o.get('actionable', False)),
            'total_pairs': len(opportunities)
        }
        
        # ─── Guardar en caché ───
        self._cache = result
        self._cache_time = now
        return result
    
    def _get_prediction(self, pair: str) -> Optional[Dict]:
        try:
            active_model = self.registry.get_active(pair, 'xgboost')
            if not active_model:
                return None
            
            result = self.data_provider.get_historical(pair, period="1y")
            df = result['data']
            df_feat = TechnicalFeatures.generate(df)
            feature_cols = TechnicalFeatures.get_feature_names()
            latest = df_feat.iloc[-1:][feature_cols].dropna()
            
            if latest.empty:
                return None
            
            model = XGBoostModel(active_model['path'])
            if model.model is None:
                return None
            
            pred = model.predict(latest)
            filtered = self.economic_filter.apply(pred)
            
            probability = filtered.get('probability', 0.5)
            edge_ratio = filtered.get('edge_ratio', 0)
            confidence = filtered.get('confidence', 0)
            
            opportunity_score = (probability * 0.6) + (min(edge_ratio / 3.0, 1.0) * 0.4)
            opportunity_score = min(max(opportunity_score, 0), 1)
            
            decision_quality = 'HIGH' if confidence > 0.7 else 'MEDIUM' if confidence > 0.4 else 'LOW'
            
            return {
                'pair': pair,
                'direction': filtered.get('direction', 'UP'),
                'opportunity_score': opportunity_score,
                'edge_ratio': edge_ratio,
                'actionable': filtered.get('actionable', False),
                'confidence': confidence,
                'decision_quality': decision_quality,
                'position_size': filtered.get('position_size', 0)
            }
        except Exception as e:
            print(f"⚠️ Error en {pair}: {e}")
            return None
