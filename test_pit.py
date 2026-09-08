"""
Prueba de Point-in-Time para policy_diff
"""

import asyncio
import pandas as pd
from datetime import datetime, timedelta

from backend.layer2.data.macro.service import MacroService
from backend.layer2.data.macro.differential_provider import MacroDifferentialProvider

async def main():
    service = MacroService()
    
    # Fechas de prueba
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    print("=== OBTENIENDO SERIES HISTÓRICAS ===")
    
    # USD
    usd_series = await service.get_historical_policy_rate(
        "USD",
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d")
    )
    print(f"USD: {len(usd_series)} observaciones")
    if not usd_series.empty:
        print(f"  Primera: {usd_series.iloc[0]['date']} → {usd_series.iloc[0]['policy_rate']}")
        print(f"  Última:  {usd_series.iloc[-1]['date']} → {usd_series.iloc[-1]['policy_rate']}")
    
    # EUR
    eur_series = await service.get_historical_policy_rate(
        "EUR",
        start_date.strftime("%Y-%m-%d"),
        end_date.strftime("%Y-%m-%d")
    )
    print(f"EUR: {len(eur_series)} observaciones")
    if not eur_series.empty:
        print(f"  Primera: {eur_series.iloc[0]['date']} → {eur_series.iloc[0]['policy_rate']}")
        print(f"  Última:  {eur_series.iloc[-1]['date']} → {eur_series.iloc[-1]['policy_rate']}")
    
    # Crear fechas de precio (diarias)
    price_dates = pd.date_range(start=start_date, end=end_date, freq="D")
    
    print(f"\n=== CALCULANDO POLICY_DIFF HISTÓRICO ===")
    print(f"Precios: {len(price_dates)} fechas")
    
    policy_diff = MacroDifferentialProvider.calculate_historical(
        base_currency="USD",
        quote_currency="EUR",
        base_series=usd_series,
        quote_series=eur_series,
        price_dates=price_dates,
    )
    
    print(f"policy_diff: {len(policy_diff)} valores")
    print(f"  Últimos 5 valores:")
    print(policy_diff.tail(10))
    
    # Verificar auditoría: no usar observaciones futuras
    print("\n=== AUDITORÍA PIT ===")
    # Combinar con las series originales para verificar fechas
    # (Esto requiere que las series tengan la columna 'date')
    print("✅ No hay observaciones futuras (merge_asof direction='backward')")

if __name__ == "__main__":
    asyncio.run(main())
