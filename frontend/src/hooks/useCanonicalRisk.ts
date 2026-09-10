/**
 * useCanonicalRisk — Canonical Risk Assessment hook.
 *
 * Consumes the v2.3 canonical endpoint:
 *   GET /v1/canonical/{pair}/risk?horizon_days={h}
 *
 * ⚠️  This hook is PURE TRANSPORT + TYPING.
 *     It does NOT compute risk_score, risk_level, or contributions.
 *     All analytical values come from the backend (RiskEngine v2.3.0).
 */
import { useQuery, type UseQueryResult } from "@tanstack/react-query";
import { apiClient } from "../services/api";

// ─── Contract types (mirror backend v2.3.0) ────────────────────────

export type RiskLevel = "LOW" | "MODERATE" | "HIGH" | "EXTREME";

export interface RiskDriver {
  name: string;                // volatility | macro | model | regime | edge
  contribution: number;        // points contributed to risk_score
  normalized_value: number;    // [0, 1]
  weight: number;              // [0, 1]
  explanation: string;         // human-readable
}

export interface RiskAssessment {
  risk_score: number;          // [0, 100]
  risk_level: RiskLevel;
  drivers: RiskDriver[];       // exactly 5
  methodology_version: string; // e.g. "v2.3.0"
}

export interface MacroDataStatusRisk {
  status?: string;             // FULL | PARTIAL | UNAVAILABLE
  base?: string;
  quote?: string;
  [key: string]: unknown;
}

export interface DecisionSummaryRisk {
  actionable?: boolean;
  signal_validity?: string;
  direction?: string;
  edge_ratio?: number;
  [key: string]: unknown;
}

export interface CanonicalRiskResponse {
  pair: string;
  horizon_days: number;
  risk: RiskAssessment;
  macro_data_status: MacroDataStatusRisk | null;
  decision_summary: DecisionSummaryRisk | null;
  timestamp: string;
}

// ─── Hook ──────────────────────────────────────────────────────────

export function useCanonicalRisk(
  pair: string,
  horizonDays: number = 30,
): UseQueryResult<CanonicalRiskResponse, Error> {
  const url = `/v1/canonical/${pair}/risk?horizon_days=${horizonDays}`;

  return useQuery<CanonicalRiskResponse, Error>({
    queryKey: ["canonical-risk", pair, horizonDays],
    queryFn: async () => {
      const response = await apiClient.get<CanonicalRiskResponse>(url);
      return response.data;
    },
    staleTime: 60_000,      // 60s — risk assessment changes slowly
    refetchInterval: 60_000,
    enabled: Boolean(pair),
    retry: 1,
  });
}
