from twelvedata import TDClient
import pandas as pd
from ...config import TWELVE_DATA_KEY

class TwelveDataSource:
    @staticmethod
    def fetch(pair: str, period: str = "1y", interval: str = "1d"):
        """Fetch data from Twelve Data."""
        client = TDClient(apikey=TWELVE_DATA_KEY)
        
        # Mapear intervalo
        interval_map = {"1d": "1day", "1h": "1h", "15m": "15min"}
        td_interval = interval_map.get(interval, "1day")
        
        # Usar outputsize=5000 para obtener más datos
        outputsize = 5000
        
        print(f"   Twelve: buscando {pair}, outputsize={outputsize}")
        
        ts = client.time_series(
            symbol=pair,
            interval=td_interval,
            outputsize=outputsize
        )
        
        df = ts.as_pandas()
        if df.empty or len(df) < 10:
            raise Exception(f"No data from Twelve Data for {pair}")
        
        # Renombrar columnas
        rename_map = {
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume'
        }
        df = df.rename(columns=rename_map)
        
        # Asegurar columnas
        required = ['Open', 'High', 'Low', 'Close']
        for col in required:
            if col not in df.columns:
                df[col] = df['Close'] if 'Close' in df.columns else 0
        
        if 'Volume' not in df.columns:
            df['Volume'] = 0
        
        # Convertir a float
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Eliminar NaN extremos
        df = df.dropna(subset=['Close'])
        
        print(f"   Twelve: {len(df)} filas obtenidas")
        return df
