/**
 * Performance domain endpoint adapter.
 *
 * Returns the raw backend response without transformation.
 */
import { apiClient } from "./api";
import type { PerformanceResponse } from "../types";

/** Fetches performance metrics for a pair and period. Layer 1 v5.1 §3, §7.4. */
export async function getPerformance(pair: string, period: string): Promise<PerformanceResponse> {
  const { data } = await apiClient.get<PerformanceResponse>(`/v1/fx/performance/${pair}`, {
    params: { period },
  });
  return data;
}