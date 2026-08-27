/**
 * Drivers domain endpoint adapter.
 *
 * Returns the raw backend response without transformation.
 */
import { apiClient } from "./api";
import type { DriversResponse } from "../types";

/** Fetches the driver explanation for a currency pair. Layer 1 v5.1 §3, §7.2. */
export async function getDrivers(pair: string): Promise<DriversResponse> {
  const { data } = await apiClient.get<DriversResponse>(`/v1/fx/${pair}/drivers`);
  return data;
}