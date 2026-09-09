/**
 * Performance period selection — composition (UI/Navigation) only.
 *
 * Reads/writes the `period` search param and validates against the contract
 * enum (PerformancePeriod). Navigation state only — no analytical logic.
 */
import { useSearchParams } from "react-router-dom";
import type { PerformancePeriod } from "../types";

/** Periods accepted by the backend (Layer 1 v5.1 §7.4). */
export const PERFORMANCE_PERIODS: PerformancePeriod[] = ["1M", "3M", "6M", "1Y", "ALL"];

/** Default period when no `period` param is present. */
export const DEFAULT_PERFORMANCE_PERIOD: PerformancePeriod = "6M";

interface PerformancePeriodState {
  /** Currently selected period (always a valid contract period). */
  period: PerformancePeriod;
  /** Updates the `period` search param (navigation only). */
  setPeriod: (next: PerformancePeriod) => void;
}

/** Navigation-bound performance period. */
export function usePerformancePeriod(): PerformancePeriodState {
  const [searchParams, setSearchParams] = useSearchParams();

  const raw = searchParams.get("period");
  const period: PerformancePeriod =
    (PERFORMANCE_PERIODS as string[]).includes(raw ?? "") ? (raw as PerformancePeriod) : DEFAULT_PERFORMANCE_PERIOD;

  const setPeriod = (next: PerformancePeriod): void => {
    const params = new URLSearchParams(searchParams);
    params.set("period", next);
    setSearchParams(params, { replace: false });
  };

  return { period, setPeriod };
}