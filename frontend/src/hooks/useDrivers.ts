/**
 * Drivers data-fetching hook.
 *
 * Returns the raw backend response without transformation.
 */
import { useQuery, type UseQueryResult } from "@tanstack/react-query";
import { getDrivers } from "../services";
import type { DriversResponse } from "../types";

/** Fetches the driver explanation for a currency pair. */
export function useDrivers(pair: string): UseQueryResult<DriversResponse> {
  return useQuery<DriversResponse>({
    queryKey: ["drivers", pair],
    queryFn: () => getDrivers(pair),
  });
}