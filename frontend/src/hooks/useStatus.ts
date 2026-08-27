/**
 * System status data-fetching hook.
 *
 * Returns the raw backend response without transformation.
 */
import { useQuery, type UseQueryResult } from "@tanstack/react-query";
import { getStatus } from "../services";
import type { StatusResponse } from "../types";

/** Fetches the consolidated system status. */
export function useStatus(): UseQueryResult<StatusResponse> {
  return useQuery<StatusResponse>({
    queryKey: ["status"],
    queryFn: () => getStatus(),
  });
}