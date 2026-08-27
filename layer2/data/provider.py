"""
Data Provider con fallback entre múltiples fuentes.
Alpha Vantage → Twelve Data → Yahoo Finance
"""
import pandas as pd
from datetime import datetime
from .sources.twelve import TwelveDataSource
from .sources.alpha_vantage import AlphaVantageSource
from .sources.yahoo import YahooSource

class DataProvider:
    def __init__(self):
        # Orden: Alpha → Twelve → Yahoo (Alpha tiene más datos históricos)
        self.sources = [
            ('alpha', AlphaVantageSource.fetch),
            ('twelve', TwelveDataSource.fetch),
            ('yahoo', YahooSource.fetch)
        ]
        self.last_provider = None
        self.last_success = None
        self.fallback_used = False
    
    def get_historical(self, pair: str, period: str = "1y", interval: str = "1d") -> dict:
        for source_name, source_func in self.sources:
            try:
                print(f"📥 Intentando {source_name}...")
                df = source_func(pair, period, interval)
                if df is not None and not df.empty and len(df) > 20:
                    self.last_provider = source_name
                    self.last_success = datetime.now()
                    self.fallback_used = (source_name != self.sources[0][0])
                    
                    last_date = df.index[-1]
                    days_ago = (datetime.now() - last_date).days
                    freshness = "FRESH" if days_ago <= 1 else "STALE" if days_ago <= 5 else "OLD"
                    
                    print(f"✅ {source_name} funcionó ({len(df)} filas)")
                    
                    return {
                        'data': df,
                        'provider': source_name,
                        'fallback_used': self.fallback_used,
                        'timestamp': datetime.now(),
                        'freshness': freshness,
                        'last_price': float(df['Close'].iloc[-1]),
                        'last_date': last_date
                    }
            except Exception as e:
                print(f"⚠️ {source_name} falló: {str(e)[:100]}")
                continue
        
        raise Exception("Todas las fuentes de datos fallaron")
    
    def get_latest_price(self, pair: str) -> float:
        result = self.get_historical(pair, period="5d", interval="1d")
        return result['last_price']
    
    def get_status(self) -> dict:
        return {
            'last_provider': self.last_provider,
            'last_success': self.last_success.isoformat() if self.last_success else None,
            'fallback_used': self.fallback_used,
            'sources_available': [s[0] for s in self.sources],
            'status': 'HEALTHY' if self.last_success else 'UNKNOWN'
        }
