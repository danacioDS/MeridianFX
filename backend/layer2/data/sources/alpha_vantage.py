from alpha_vantage.foreignexchange import ForeignExchange
import pandas as pd
from ...config import ALPHA_VANTAGE_KEY

class AlphaVantageSource:
    @staticmethod
    def fetch(pair: str, period: str = "1y", interval: str = "1d"):
        """Fetch data from Alpha Vantage."""
        from_currency, to_currency = pair.split("/")
        client = ForeignExchange(key=ALPHA_VANTAGE_KEY)
        
        print(f"   Alpha: buscando {from_currency}/{to_currency}, outputsize=full")
        
        try:
            data, meta = client.get_currency_exchange_daily(
                from_symbol=from_currency,
                to_symbol=to_currency,
                outputsize='full'  # Obtener todos los datos disponibles
            )
            
            if not data:
                raise Exception(f"No data from Alpha Vantage for {pair}")
            
            df = pd.DataFrame.from_dict(data, orient='index')
            df.index = pd.to_datetime(df.index)
            df = df.sort_index()
            
            rename_map = {
                '1. open': 'Open',
                '2. high': 'High',
                '3. low': 'Low',
                '4. close': 'Close',
                '5. volume': 'Volume'
            }
            df = df.rename(columns=rename_map)
            
            required = ['Open', 'High', 'Low', 'Close']
            for col in required:
                if col not in df.columns:
                    df[col] = df['Close'] if 'Close' in df.columns else 0
            
            if 'Volume' not in df.columns:
                df['Volume'] = 0
            
            for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df = df.dropna(subset=['Close'])
            print(f"   Alpha: {len(df)} filas obtenidas")
            return df.tail(500)
            
        except Exception as e:
            print(f"   Alpha error: {e}")
            raise
