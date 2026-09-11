/**
 * usePrice — Spot price + historical OHLCV.
 *
 * Consumes: GET /v1/fx/{pair}/price?period={period}
 */
import { useQuery, type UseQueryResult } from "@tanstack/react-query";
import type { PriceResponse } from "../types";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function fetchPrice(pair: string, period: string): Promise<PriceResponse> {
  const response = await fetch(`${API_URL}/v1/fx/${pair}/price?period=${period}`);
  if (!response.ok) {
    throw new Error(`Error ${response.status}: ${response.statusText}`);
  }
  return response.json();
}

export function usePrice(
  pair: string,
  period: string = "1y"
): UseQueryResult<PriceResponse, Error> {
  return useQuery<PriceResponse, Error>({
    queryKey: ["price", pair, period],
    queryFn: () => fetchPrice(pair, period),
    enabled: !!pair,
    refetchInterval: 5 * 60 * 1000, // 5 min
    staleTime: 5 * 60 * 1000,       // 5 min
  });
}
