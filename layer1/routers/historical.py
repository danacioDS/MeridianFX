from fastapi import APIRouter, Path, Query
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from ..models.responses import DriversResponse
from layer2.engine import DecisionEngine
from layer2.data.provider import DataProvider
from layer2.features.technical import TechnicalFeatures

router = APIRouter(prefix="/v1/fx", tags=["historical"])
engine = DecisionEngine()
data_provider = DataProvider()

@router.get("/{pair:path}/historical")
async def get_historical(
    pair: str = Path(..., description="Currency pair (e.g., USD/JPY)"),
    period: str = Query("1y", description="Period: 1y, 3y, 5y, 10y")
):
    """Obtiene datos históricos con features calculados."""
    try:
        # Mapear período
        period_map = {
            "1y": "1y",
            "3y": "3y", 
            "5y": "5y",
            "10y": "10y"
        }
        yf_period = period_map.get(period, "1y")
        
        # Obtener datos históricos
        result = data_provider.get_historical(pair, period=yf_period)
        df = result['data']
        
        # Generar features
        df_feat = TechnicalFeatures.generate(df)
        
        # Preparar datos para el frontend
        prices = []
        features = []
        
        # Obtener fechas
        dates = df.index.tolist()
        
        # Para cada fecha, extraer precio y features
        for i, date in enumerate(dates):
            price_data = {
                'date': date.strftime('%Y-%m-%d'),
                'close': float(df['Close'].iloc[i])
            }
            prices.append(price_data)
            
            # Features si están disponibles
            if i < len(df_feat):
                feat_row = df_feat.iloc[i]
                features.append({
                    'rsi_14': float(feat_row['rsi_14']) if pd.notna(feat_row.get('rsi_14')) else None,
                    'macd': float(feat_row['macd']) if pd.notna(feat_row.get('macd')) else None,
                    'volatility': float(feat_row['volatility']) if pd.notna(feat_row.get('volatility')) else None,
                    'sma_50': float(feat_row['sma_50']) if pd.notna(feat_row.get('sma_50')) else None,
                    'sma_200': float(feat_row['sma_200']) if pd.notna(feat_row.get('sma_200')) else None,
                })
            else:
                features.append({
                    'rsi_14': None,
                    'macd': None,
                    'volatility': None,
                    'sma_50': None,
                    'sma_200': None,
                })
        
        # Tomar solo los últimos puntos para no sobrecargar
        max_points = 500
        if len(prices) > max_points:
            step = len(prices) // max_points
            prices = prices[::step][:max_points]
            features = features[::step][:max_points]
        
        return {
            'pair': pair,
            'prices': prices,
            'features': features,
            'meta': {
                'provider': result['provider'],
                'fallback_used': result['fallback_used'],
                'freshness': result['freshness'],
                'last_price': float(df['Close'].iloc[-1]),
                'last_date': df.index[-1].strftime('%Y-%m-%d')
            }
        }
        
    except Exception as e:
        print(f"❌ Error en historical: {e}")
        # Devolver datos de ejemplo si falla
        return _get_fallback_historical(pair)

def _get_fallback_historical(pair: str):
    """Datos de ejemplo cuando falla la API."""
    dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
    prices = []
    features = []
    
    base_price = 150.0
    for i, date in enumerate(dates):
        variation = np.random.randn() * 0.5
        base_price = max(140, base_price + variation)
        prices.append({
            'date': date.strftime('%Y-%m-%d'),
            'close': round(base_price, 2)
        })
        features.append({
            'rsi_14': round(50 + np.random.randn() * 15, 2),
            'macd': round(np.random.randn() * 0.5, 3),
            'volatility': round(0.1 + np.random.rand() * 0.2, 3),
            'sma_50': round(base_price + np.random.randn() * 2, 2),
            'sma_200': round(base_price + np.random.randn() * 5, 2),
        })
    
    return {
        'pair': pair,
        'prices': prices,
        'features': features,
        'meta': {
            'provider': 'fallback',
            'fallback_used': True,
            'freshness': 'OLD',
            'last_price': prices[-1]['close'],
            'last_date': prices[-1]['date']
        }
    }
