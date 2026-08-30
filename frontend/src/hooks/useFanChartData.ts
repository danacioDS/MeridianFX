import { useQuery } from '@tanstack/react-query';
import type { ForecastResponse } from '../types/contracts';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function fetchForecast(pair: string): Promise<ForecastResponse> {
  // Construir URL con el formato correcto: /v1/fx/USD/JPY/forecast
  const [base, quote] = pair.split('/');
  const response = await fetch(`${API_URL}/v1/fx/${base}/${quote}/forecast`);
  if (!response.ok) {
    throw new Error(`Error ${response.status}: ${response.statusText}`);
  }
  return response.json();
}

export interface FanChartPoint {
  date: string;
  p10: number;
  p25: number;
  p50: number;
  p75: number;
  p90: number;
  actual?: number;
}

export function useFanChartData(pair: string) {
  return useQuery({
    queryKey: ['fan-chart', pair],
    queryFn: () => fetchForecast(pair),
    enabled: !!pair,
    refetchInterval: 60000,
    staleTime: 30000,
  });
}

export function transformToFanChartData(
  forecast: ForecastResponse,
  currentPrice: number,
  currentDate: string
): FanChartPoint[] {
  const prediction = forecast?.prediction;
  
  if (!prediction) {
    return [];
  }

  const expectedReturn = prediction.expected_return || 0;
  const volatility = prediction.expected_volatility || 0.01;
  
  // Generar puntos para 30, 60, 90 días
  const horizons = [30, 60, 90];
  const now = new Date(currentDate);
  
  return horizons.map((days) => {
    const date = new Date(now);
    date.setDate(date.getDate() + days);
    
    // Escalar retorno y volatilidad con el tiempo
    const scaledReturn = expectedReturn * (days / 30);
    const scaledVol = volatility * Math.sqrt(days / 30);
    
    // P50 (mediana)
    const p50 = currentPrice * (1 + scaledReturn);
    
    // Asumiendo distribución normal para P10, P25, P75, P90
    const z_p90 = 1.282; // 90% CI
    const z_p75 = 0.674; // 75% CI
    const z_p25 = -0.674;
    const z_p10 = -1.282;
    
    return {
      date: date.toISOString().split('T')[0],
      p10: p50 * (1 + z_p10 * scaledVol),
      p25: p50 * (1 + z_p25 * scaledVol),
      p50: p50,
      p75: p50 * (1 + z_p75 * scaledVol),
      p90: p50 * (1 + z_p90 * scaledVol),
    };
  });
}
