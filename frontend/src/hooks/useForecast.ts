/**
 * useForecast — Latest forecast for a currency pair.
 *
 * Consumes: GET /v1/fx/{pair}/forecast
 */
import { useQuery, type UseQueryResult } from "@tanstack/react-query";
import { getForecast } from "../services/forecast";
import type { ForecastResponse } from "../types";

export function useForecast(pair: string): UseQueryResult<ForecastResponse, Error> {
  return useQuery<ForecastResponse, Error>({
    queryKey: ["forecast", pair],
    queryFn: () => getForecast(pair),
    enabled: !!pair,
    refetchInterval: 30000,
    retry: 1,
  });
}
