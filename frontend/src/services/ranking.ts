/**
 * Ranking domain endpoint adapter.
 *
 * Returns the raw backend response without transformation.
 * Ranking order is owned by Layer 2; Layer 1 delivers it verbatim.
 */
import { apiClient } from "./api";
import type { RankingResponse } from "../types";

/** Fetches the opportunity ranking snapshot. Layer 1 v5.1 §3, §7.3. */
export async function getRanking(): Promise<RankingResponse> {
  const { data } = await apiClient.get<RankingResponse>("/v1/fx/ranking");
  return data;
}