/**
 * Forecast data-fetching hook.
 *
 * Returns the raw backend response without transformation.
 * NOTE: useForecastHistory is UNSUPPORTED_BY_CONTRACT (see CONTRACT_GAPS.md, G1).
 */
import { useQuery, type UseQueryResult } from "@tanstack/react-query";
import { getForecast } from "../services";
import type { ForecastResponse } from "../types";

/** Fetches the latest forecast for a currency pair. */
export function useForecast(pair: string): UseQueryResult<ForecastResponse> {
  return useQuery<ForecastResponse>({
    queryKey: ["forecast", pair],
    queryFn: () => getForecast(pair),
  });
}