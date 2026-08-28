"""
Ranking Engine - Genera ranking de oportunidades.
"""
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
        
        # Obtener todos los pares que tienen modelo registrado
        all_pairs = ['USD/JPY', 'EUR/USD', 'GBP/USD', 'USD/CNY', 'USD/MXN', 
                     'USD/BRL', 'USD/ARS', 'USD/BOB', 'USD/CHF']
        
        # Filtrar solo pares con modelo activo
        self.pairs = []
        for pair in all_pairs:
            active = self.registry.get_active(pair, 'xgboost')
            if active:
                self.pairs.append(pair)
                print(f"✅ {pair}: modelo activo encontrado")
            else:
                print(f"⚠️ {pair}: sin modelo activo")
        
        print(f"📊 Pares con modelo: {len(self.pairs)}")
    
    def get_ranking(self) -> Dict:
        """Genera ranking completo de oportunidades."""
        opportunities = []
        
        for pair in self.pairs:
            try:
                result = self._get_prediction_for_pair(pair)
                if result:
                    opportunities.append(result)
            except Exception as e:
                print(f"⚠️ Error en {pair}: {e}")
                continue
        
        # Ordenar por opportunity_score
        opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
        
        # Asignar ranks
        for i, opp in enumerate(opportunities):
            opp['rank'] = i + 1
        
        total_actionable = sum(1 for o in opportunities if o.get('actionable', False))
        
        return {
            'timestamp': datetime.now().isoformat(),
            'opportunities': opportunities,
            'top_opportunity': opportunities[0] if opportunities else None,
            'total_actionable': total_actionable,
            'total_pairs': len(opportunities),
        }
    
    def _get_prediction_for_pair(self, pair: str) -> Optional[Dict]:
        """Obtiene predicción para un par."""
        try:
            # 1. Obtener modelo activo
            active_model = self.registry.get_active(pair, 'xgboost')
            if not active_model:
                return None
            
            # 2. Obtener datos históricos
            result = self.data_provider.get_historical(pair, period="1y")
            df = result['data']
            
            if df.empty or len(df) < 50:
                return None
            
            # 3. Generar features
            df_feat = TechnicalFeatures.generate(df)
            feature_cols = TechnicalFeatures.get_feature_names()
            latest = df_feat.iloc[-1:][feature_cols].dropna()
            
            if latest.empty:
                return None
            
            # 4. Cargar modelo
            model = XGBoostModel(active_model['path'])
            if model.model is None:
                return None
            
            # 5. Predecir
            pred = model.predict(latest)
            
            # 6. Aplicar filtro económico
            filtered = self.economic_filter.apply(pred)
            
            probability = filtered.get('probability', 0.5)
            edge_ratio = filtered.get('edge_ratio', 0)
            confidence = filtered.get('confidence', 0)
            
            # Calcular opportunity_score
            edge_normalized = min(edge_ratio / 3.0, 1.0)
            opportunity_score = (probability * 0.6) + (edge_normalized * 0.4)
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
                'position_size': filtered.get('position_size', 0),
                'probability': probability,
                'model_available': True,
            }
            
        except Exception as e:
            print(f"⚠️ Error en _get_prediction_for_pair({pair}): {e}")
            return None
