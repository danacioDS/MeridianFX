/**
 * Frontend infrastructure types.
 *
 * These types represent request/UI infrastructure only. They MUST NOT be used
 * to redefine, wrap, or reinterpret Layer 1 domain contracts. ApiResponse<T> is
 * intentionally NOT defined: Layer 1 v5.1 does not return a response envelope,
 * so services return domain types directly.
 */

/** Async request lifecycle status (frontend-only). */
export type ApiStatus = "IDLE" | "LOADING" | "SUCCESS" | "ERROR";

/** Polling / refetch configuration (frontend-only). */
export interface PollingConfig {
  /** Interval between polls, in milliseconds. */
  interval: number;
  /** Whether polling is enabled. */
  enabled: boolean;
}