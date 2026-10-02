/**
 * useSystemTrace — Architecture Control Center hook.
 *
 * Consumes: GET /v1/system/trace?pair={pair}
 *
 * Pure transport. The backend composes the four layer endpoints
 * into a single payload; this hook does not aggregate anything.
 */
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../services/api";
import type { SystemTrace } from "../types/system";

export function useSystemTrace(pair: string) {
  return useQuery({
    queryKey: ["system-trace", pair],
    queryFn: async () => {
      const { data } = await apiClient.get<SystemTrace>("/v1/system/trace", {
        params: { pair },
      });
      return data;
    },
    staleTime: 60_000,
  });
}
