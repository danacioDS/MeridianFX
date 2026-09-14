/**
 * useCanonicalNarrative — Persistent LLM narrative for a canonical decision.
 *
 * Consumes: GET /v1/canonical/{pair}/narrative?horizon_days={h}
 *
 * ⚠️  PURE TRANSPORT. No transformation, no derivation.
 *     The narrative is generated and cached by the backend.
 */
import { useQuery, type UseQueryResult } from "@tanstack/react-query";
import { apiClient } from "../services/api";

export interface NarrativeCacheInfo {
  hit: boolean;
  persisted?: boolean;
}

export interface CanonicalNarrative {
  pair: string;
  horizon_days: number;
  narrative_key: string;
  prompt_version: string;
  narrative: string;
  provider: string;
  model: string;
  generated_at: string | null;
  last_served_at: string | null;
  generation_count: number;
  served_count: number;
  cache: NarrativeCacheInfo;
}

export function useCanonicalNarrative(
  pair: string,
  horizonDays: number = 5
): UseQueryResult<CanonicalNarrative, Error> {
  return useQuery<CanonicalNarrative, Error>({
    queryKey: ["canonical-narrative", pair, horizonDays],
    queryFn: async () => {
      const response = await apiClient.get<CanonicalNarrative>(
        `/v1/canonical/${pair}/narrative`,
        { params: { horizon_days: horizonDays } }
      );
      return response.data;
    },
    enabled: !!pair,
    staleTime: 5 * 60 * 1000,
  });
}
