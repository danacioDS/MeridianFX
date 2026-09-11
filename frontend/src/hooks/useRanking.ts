/**
 * useRanking — FX ranking of opportunities.
 *
 * Consumes: GET /v1/fx/ranking
 */
import { useQuery, type UseQueryResult } from "@tanstack/react-query";
import type { RankingResponse } from "../types";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function fetchRanking(): Promise<RankingResponse> {
  const response = await fetch(`${API_URL}/v1/fx/ranking`);
  if (!response.ok) {
    throw new Error(`Error ${response.status}: ${response.statusText}`);
  }
  return response.json();
}

export function useRanking(): UseQueryResult<RankingResponse, Error> {
  return useQuery<RankingResponse, Error>({
    queryKey: ["ranking"],
    queryFn: fetchRanking,
    refetchInterval: 5 * 60 * 1000,  // 5 min
    staleTime: 5 * 60 * 1000,      // 5 min
  });
}
