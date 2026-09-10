/**
 * usePrice — Spot price + historical OHLCV.
 *
 * Consumes: GET /v1/fx/{pair}/price?period={period}
 *
 * ⚠️  Types are defined locally in MarketPage.
 *     This hook stays untyped to avoid breaking legacy pages that
 *     access fields not in the canonical price contract.
 */
import { useQuery } from "@tanstack/react-query";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function fetchPrice(pair: string, period: string) {
  const response = await fetch(`${API_URL}/v1/fx/${pair}/price?period=${period}`);
  if (!response.ok) {
    throw new Error(`Error ${response.status}: ${response.statusText}`);
  }
  return response.json();
}

export function usePrice(pair: string, period: string = "1y") {
  return useQuery({
    queryKey: ["price", pair, period],
    queryFn: () => fetchPrice(pair, period),
    enabled: !!pair,
    refetchInterval: 60000,
    staleTime: 30000,
  });
}
