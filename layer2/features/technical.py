import pandas as pd
import numpy as np
import pandas_ta as ta

class TechnicalFeatures:
    @staticmethod
    def generate(df: pd.DataFrame) -> pd.DataFrame:
        """Genera todos los indicadores técnicos."""
        df = df.copy()
        
        # Asegurar que tenemos suficientes datos
        if len(df) < 50:
            print(f"⚠️ Datos insuficientes: {len(df)} filas, mínimo 50")
            return pd.DataFrame()
        
        # Medias móviles
        df['sma_10'] = ta.sma(df['Close'], length=10)
        df['sma_20'] = ta.sma(df['Close'], length=20)
        df['sma_50'] = ta.sma(df['Close'], length=50)
        df['sma_200'] = ta.sma(df['Close'], length=200)
        df['ema_12'] = ta.ema(df['Close'], length=12)
        df['ema_26'] = ta.ema(df['Close'], length=26)
        
        # RSI
        df['rsi_14'] = ta.rsi(df['Close'], length=14)
        
        # MACD
        macd = ta.macd(df['Close'])
        if macd is not None and not macd.empty:
            cols = macd.columns.tolist()
            # Buscar columnas por nombre o posición
            if len(cols) >= 3:
                df['macd'] = macd[cols[0]]
                df['macd_signal'] = macd[cols[1]]
                df['macd_hist'] = macd[cols[2]]
            else:
                df['macd'] = np.nan
                df['macd_signal'] = np.nan
                df['macd_hist'] = np.nan
        else:
            df['macd'] = np.nan
            df['macd_signal'] = np.nan
            df['macd_hist'] = np.nan
        
        # Bollinger Bands
        bbands = ta.bbands(df['Close'])
        if bbands is not None and not bbands.empty:
            cols = bbands.columns.tolist()
            # Buscar por nombre o usar posición
            upper = [c for c in cols if 'BBU' in c or 'upper' in c.lower()]
            middle = [c for c in cols if 'BBM' in c or 'middle' in c.lower()]
            lower = [c for c in cols if 'BBL' in c or 'lower' in c.lower()]
            
            if upper:
                df['bb_upper'] = bbands[upper[0]]
            elif len(cols) >= 3:
                df['bb_upper'] = bbands[cols[0]]
            else:
                df['bb_upper'] = np.nan
                
            if middle:
                df['bb_middle'] = bbands[middle[0]]
            elif len(cols) >= 3:
                df['bb_middle'] = bbands[cols[1]]
            else:
                df['bb_middle'] = np.nan
                
            if lower:
                df['bb_lower'] = bbands[lower[0]]
            elif len(cols) >= 3:
                df['bb_lower'] = bbands[cols[2]]
            else:
                df['bb_lower'] = np.nan
            
            # BB width
            width = [c for c in cols if 'BBW' in c or 'width' in c.lower()]
            if width:
                df['bb_width'] = bbands[width[0]]
            elif len(cols) >= 4:
                df['bb_width'] = bbands[cols[3]]
            else:
                df['bb_width'] = np.nan
        else:
            df['bb_upper'] = np.nan
            df['bb_middle'] = np.nan
            df['bb_lower'] = np.nan
            df['bb_width'] = np.nan
        
        # ATR
        atr_result = ta.atr(df['High'], df['Low'], df['Close'])
        if atr_result is not None and not atr_result.empty:
            df['atr'] = atr_result
        else:
            df['atr'] = np.nan
        
        # Momentum
        df['momentum'] = ta.mom(df['Close'])
        df['roc'] = ta.roc(df['Close'])
        
        # Volatilidad
        df['volatility'] = df['Close'].pct_change().rolling(20).std()
        
        # ADX
        adx = ta.adx(df['High'], df['Low'], df['Close'])
        if adx is not None and not adx.empty:
            cols = adx.columns.tolist()
            adx_cols = [c for c in cols if 'ADX' in c]
            if adx_cols:
                df['adx'] = adx[adx_cols[0]]
            else:
                df['adx'] = np.nan
        else:
            df['adx'] = np.nan
        
        # Aroon
        aroon = ta.aroon(df['High'], df['Low'])
        if aroon is not None and not aroon.empty:
            cols = aroon.columns.tolist()
            up = [c for c in cols if 'AROONU' in c or 'up' in c.lower()]
            down = [c for c in cols if 'AROOND' in c or 'down' in c.lower()]
            if up:
                df['aroon_up'] = aroon[up[0]]
            else:
                df['aroon_up'] = np.nan
            if down:
                df['aroon_down'] = aroon[down[0]]
            else:
                df['aroon_down'] = np.nan
        else:
            df['aroon_up'] = np.nan
            df['aroon_down'] = np.nan
        
        # Stochastic
        stoch = ta.stoch(df['High'], df['Low'], df['Close'])
        if stoch is not None and not stoch.empty:
            cols = stoch.columns.tolist()
            k = [c for c in cols if 'STOCHk' in c or 'K' in c]
            d = [c for c in cols if 'STOCHd' in c or 'D' in c]
            if k:
                df['stoch_k'] = stoch[k[0]]
            else:
                df['stoch_k'] = np.nan
            if d:
                df['stoch_d'] = stoch[d[0]]
            else:
                df['stoch_d'] = np.nan
        else:
            df['stoch_k'] = np.nan
            df['stoch_d'] = np.nan
        
        # Eliminar filas con NaN (más tolerante)
        # Solo eliminar si más del 50% de features son NaN
        feature_cols = TechnicalFeatures.get_feature_names()
        df_features = df[feature_cols]
        
        # Contar NaN por fila
        nan_count = df_features.isna().sum(axis=1)
        total_features = len(feature_cols)
        
        # Mantener filas con menos del 50% de NaN
        keep_mask = nan_count < (total_features * 0.5)
        df = df[keep_mask].copy()
        
        print(f"📈 Features generadas: {len(df)} filas")
        
        if len(df) == 0:
            print("⚠️ Todas las filas fueron eliminadas. Verificando datos...")
            print(f"   Columnas disponibles: {df.columns.tolist()[:10]}...")
            return pd.DataFrame()
        
        return df
    
    @staticmethod
    def get_feature_names() -> list:
        return [
            'sma_10', 'sma_20', 'sma_50', 'sma_200', 'ema_12', 'ema_26',
            'rsi_14', 'macd', 'macd_signal', 'macd_hist',
            'bb_upper', 'bb_middle', 'bb_lower', 'bb_width',
            'atr', 'momentum', 'roc', 'volatility',
            'adx', 'aroon_up', 'aroon_down', 'stoch_k', 'stoch_d'
        ]
    
    @staticmethod
    def create_target(df: pd.DataFrame, forward_days: int = 5) -> pd.Series:
        """Crea target: 1 si el precio sube en los próximos N días."""
        future_price = df['Close'].shift(-forward_days)
        target = (future_price > df['Close']).astype(int)
        return target
