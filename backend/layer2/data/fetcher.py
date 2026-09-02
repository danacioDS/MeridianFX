import pandas as pd
from .sources.yahoo import YahooSource
from .sources.alpha_vantage import AlphaVantageSource
from .sources.twelve import TwelveDataSource

class DataFetcher:
    def __init__(self):
        self.sources = [
            ('yahoo', YahooSource.fetch),
            ('alpha', AlphaVantageSource.fetch),
            ('twelve', TwelveDataSource.fetch)
        ]
        self.current_source = 'yahoo'
    
    def get_historical(self, pair: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """Obtiene datos históricos con failover."""
        for source_name, source_func in self.sources:
            try:
                print(f"📥 Intentando {source_name}...")
                df = source_func(pair, period, interval)
                if df is not None and not df.empty:
                    self.current_source = source_name
                    print(f"✅ {source_name} funcionó")
                    return df
            except Exception as e:
                print(f"⚠️ {source_name} falló: {e}")
                continue
        
        raise Exception("Todas las fuentes de datos fallaron")
    
    def get_latest_price(self, pair: str) -> float:
        """Obtiene el precio más reciente."""
        df = self.get_historical(pair, period="5d", interval="1d")
        return float(df['Close'].iloc[-1])
