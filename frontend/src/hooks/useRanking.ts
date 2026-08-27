/**
 * Ranking data-fetching hook.
 *
 * Returns the raw backend response without transformation.
 */
import { useQuery, type UseQueryResult } from "@tanstack/react-query";
import { getRanking } from "../services";
import type { RankingResponse } from "../types";

/** Fetches the opportunity ranking snapshot. */
export function useRanking(): UseQueryResult<RankingResponse> {
  return useQuery<RankingResponse>({
    queryKey: ["ranking"],
    queryFn: () => getRanking(),
  });
}