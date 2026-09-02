import yfinance as yf
import pandas as pd
import pytz

class YahooSource:
    @staticmethod
    def fetch(pair: str, period: str = "1y", interval: str = "1d"):
        """Fetch data from Yahoo Finance."""
        ticker = pair.replace("/", "") + "=X"  # USD/JPY → USDJPY=X
        print(f"   Yahoo: buscando {ticker}")
        
        try:
            ticker_obj = yf.Ticker(ticker)
            df = ticker_obj.history(period=period, interval=interval)
            
            if df.empty:
                raise Exception(f"No data from Yahoo for {pair}")
            
            # Asegurar que el índice es timezone-naive
            if df.index.tz is not None:
                df.index = df.index.tz_localize(None)
            
            print(f"   Yahoo: {len(df)} filas obtenidas")
            return df
            
        except Exception as e:
            print(f"   Yahoo error: {e}")
            raise
