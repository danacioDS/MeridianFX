/**
 * useRegimeDivergence — Rolling ARIMA(1,0,1) divergence for a pair.
 *
 * Consumes: GET /v1/fx/{pair}/regime-divergence?window_days=90&period=1y
 *
 * ⚠️  PURE TRANSPORT. The endpoint returns observed, projected and
 *     divergence series already computed on the backend.
 */
import { useQuery, type UseQueryResult } from "@tanstack/react-query";
import { apiClient } from "../services/api";

// Date-value pair serialized as a 2-tuple.
export type SeriesPoint = [string, number];

export interface RegimeDivergenceResponse {
  pair: string;
  regime: string;
  window_days: number;
  current_zscore: number | null;
  interpretation:
    | "normal"
    | "notable"
    | "extreme"
    | "persistent"
    | "unavailable";
  observed_series: SeriesPoint[];
  projected_series: SeriesPoint[];
  divergence_series: [string, number | null][];
  metadata: {
    provider: string;
    freshness: string;
    last_date: string;
    n_observations: number;
  };
}

export function useRegimeDivergence(
  pair: string,
  windowDays: number = 90,
  period: string = "1y"
): UseQueryResult<RegimeDivergenceResponse, Error> {
  return useQuery<RegimeDivergenceResponse, Error>({
    queryKey: ["regime-divergence", pair, windowDays, period],
    queryFn: async () => {
      const response = await apiClient.get<RegimeDivergenceResponse>(
        `/v1/fx/${pair}/regime-divergence`,
        { params: { window_days: windowDays, period } }
      );
      return response.data;
    },
    enabled: !!pair,
    staleTime: 5 * 60 * 1000,
  });
}
