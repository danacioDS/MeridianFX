/**
 * Performance data-fetching hook.
 *
 * Returns the raw backend response without transformation.
 */
import { useQuery, type UseQueryResult } from "@tanstack/react-query";
import { getPerformance } from "../services";
import type { PerformanceResponse } from "../types";

/** Fetches performance metrics for a pair and period. */
export function usePerformance(pair: string, period: string): UseQueryResult<PerformanceResponse> {
  return useQuery<PerformanceResponse>({
    queryKey: ["performance", pair, period],
    queryFn: () => getPerformance(pair, period),
  });
}