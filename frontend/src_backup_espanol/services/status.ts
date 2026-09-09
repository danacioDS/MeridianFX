/**
 * System status domain endpoint adapter.
 *
 * Returns the raw backend response without transformation.
 * NOTE: getHealth is UNSUPPORTED_BY_CONTRACT (no HealthResponse structure in
 * Layer 1 v5.1 §7 — see docs/Contract/CONTRACT_GAPS.md, G2).
 */
import { apiClient } from "./api";
import type { StatusResponse } from "../types";

/** Fetches the consolidated system status. Layer 1 v5.1 §3, §7.7. */
export async function getStatus(): Promise<StatusResponse> {
  const { data } = await apiClient.get<StatusResponse>("/v1/status");
  return data;
}