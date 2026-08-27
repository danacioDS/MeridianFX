/**
 * Forecast domain endpoint adapter.
 *
 * Returns the raw backend response without transformation.
 * NOTE: getForecastHistory is UNSUPPORTED_BY_CONTRACT (no response structure
 * in Layer 1 v5.1 §7 — see docs/Contract/CONTRACT_GAPS.md, G1).
 */
import { apiClient } from "./api";
import type { ForecastResponse } from "../types";

/** Fetches the latest forecast for a currency pair. Layer 1 v5.1 §3, §7.1. */
export async function getForecast(pair: string): Promise<ForecastResponse> {
  const { data } = await apiClient.get<ForecastResponse>(`/v1/fx/${pair}/forecast`);
  return data;
}