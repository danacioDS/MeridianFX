/**
 * Infrastructure polling hook — data-fetching ONLY.
 *
 * MAY control request/refetch timing. MUST NOT transform analytical data,
 * calculate derived metrics, infer state, modify backend responses, or
 * implement business rules. Returns the original resolved value unchanged.
 */
import { useQuery, type UseQueryResult } from "@tanstack/react-query";

/** Polls `fn` every `interval` ms while `enabled` is true. */
export function usePolling<T>(
  fn: () => Promise<T>,
  interval: number,
  enabled: boolean = true,
): UseQueryResult<T> {
  return useQuery<T>({
    queryKey: ["polling", fn],
    queryFn: fn,
    refetchInterval: interval,
    enabled,
  });
}