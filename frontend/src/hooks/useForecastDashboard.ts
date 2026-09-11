/**
 * useForecastDashboard — Consolidated market analysis hook.
 *
 * Consumes: GET /v1/fx/{pair}/forecast-dashboard
 *
 * Tipos derivados del contrato real del endpoint (Sprint 8).
 */
import { useQuery, type UseQueryResult } from "@tanstack/react-query";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// ─── Types (mirror backend v2.3.0) ─────────────────────────────────

export interface DashboardSpot {
  price: number;
  previous: number;
  change_abs: number;
  change_pct: number;
}

export interface DashboardTrend {
  return: number;
  direction: "UP" | "DOWN" | "NEUTRAL";
  strength: number;
}

export interface DashboardForecastModel {
  type: string;
  version: string;
}

export interface DashboardForecast {
  direction: "UP" | "DOWN" | "NEUTRAL";
  probability: number;
  expected_return: number;
  current_price: number;
  volatility: number;
  ci_95_lower: number;
  ci_95_upper: number;
  model: DashboardForecastModel;
}

export interface DashboardHistoryPoint {
  date: string;
  close: number;
  open: number;
  high: number;
  low: number;
}

export interface ForecastDashboard {
  pair: string;
  as_of: string;
  spot: DashboardSpot;
  trends: Record<"1m" | "3m" | "6m" | "1y", DashboardTrend>;
  volatility: number;
  forecasts: Record<"30d" | "60d" | "90d", DashboardForecast>;
  history: DashboardHistoryPoint[];
  source: string;
  freshness: string;
  last_date: string;
  macro: Record<string, unknown>;
}

// ─── Fetch ─────────────────────────────────────────────────────────

async function fetchForecastDashboard(pair: string): Promise<ForecastDashboard> {
  const response = await fetch(`${API_URL}/v1/fx/${pair}/forecast-dashboard`);
  if (!response.ok) {
    throw new Error(`Error ${response.status}: ${response.statusText}`);
  }
  return response.json();
}

// ─── Hook ──────────────────────────────────────────────────────────

export function useForecastDashboard(
  pair: string
): UseQueryResult<ForecastDashboard, Error> {
  return useQuery<ForecastDashboard, Error>({
    queryKey: ["forecast-dashboard", pair],
    queryFn: () => fetchForecastDashboard(pair),
    enabled: !!pair,
    refetchInterval: 5 * 60 * 1000, // 5 min
    staleTime: 5 * 60 * 1000,       // 5 min
  });
}
