import { useQuery, type UseQueryResult } from "@tanstack/react-query";
import { apiClient } from "../services/api";

interface HistoricalData {
  pair: string;
  prices: { date: string; close: number }[];
  features: {
    rsi_14: number | null;
    macd: number | null;
    volatility: number | null;
    sma_50: number | null;
    sma_200: number | null;
  }[];
  meta: {
    provider: string;
    fallback_used: boolean;
    freshness: string;
    last_price: number;
    last_date: string;
  };
}

// Endpoint para obtener datos históricos (lo crearemos en Layer 1)
async function getHistoricalData(pair: string, period: string = "1y"): Promise<HistoricalData> {
  const { data } = await apiClient.get<HistoricalData>(`/v1/fx/${pair}/historical`, {
    params: { period }
  });
  return data;
}

export function useHistorical(pair: string, period: string = "1y"): UseQueryResult<HistoricalData> {
  return useQuery<HistoricalData>({
    queryKey: ["historical", pair, period],
    queryFn: () => getHistoricalData(pair, period),
    staleTime: 60_000, // 1 minuto
  });
}
