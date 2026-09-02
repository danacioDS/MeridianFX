"""
Data Validator — detección de anomalías OHLC.

Importante:
Este módulo NO corrige automáticamente cambios de régimen.
Detecta saltos estadísticos para diagnóstico y auditoría.
"""

import pandas as pd


class DataValidator:

    @staticmethod
    def detect_price_jumps(
        df: pd.DataFrame,
        threshold: float = 0.50,
    ) -> pd.Series:
        """
        Detecta cambios absolutos grandes en Close.

        No modifica los datos.
        """
        diff = df["Close"].diff().abs()
        jumps = diff[diff > threshold]

        if not jumps.empty:
            print(
                f"⚠️ {len(jumps)} saltos de precio "
                f"> {threshold} detectados"
            )

            for idx, value in jumps.items():
                print(
                    f"   {idx.date()}: "
                    f"Δ={value:.4f}"
                )

        return jumps
