/**
 * useMarketIntelligence — Market Intelligence aggregate for Global.
 *
 * Consumes: GET /v1/market-intelligence?pair={pair}
 *
 * ⚠️  This hook is PURE TRANSPORT. Types are declared locally; no
 *     calculation, no aggregation, no derivation is performed.
 */
import { useQuery, type UseQueryResult } from "@tanstack/react-query";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// ─── Types (mirror backend v2.3.0+) ────────────────────────────────

export interface MISignal {
  pair: string;
  direction: string;         // "bullish" | "bearish"
  confidence: number;        // [0, 1]
  edge_ratio: number;
  opportunity_score: number;
  actionable: boolean;
}

export interface MIDecisionView {
  status: string;            // "SELECTIVE" | ...
  actionable_count: number;
  total_pairs: number;
  principle: string;
}

export interface MICurrentContext {
  market_coverage: number;
  actionable_opportunities: number;
  context: string;
}

export interface MISelectedPairView {
  pair: string;
  available: boolean;
  status?: "ACTIONABLE" | "NOT_ACTIONABLE" | "UNAVAILABLE";
  rank?: number | null;
  direction?: string;
  direction_label?: string;
  confidence?: number;
  edge_ratio?: number;
  opportunity_score?: number;
  quality?: string;
  actionable?: boolean;
  narrative?: string;
  reason?: string;
}

export interface MarketIntelligence {
  timestamp: string;
  system: string;
  language: string;
  architecture: Record<string, string>;
  current_context: MICurrentContext;
  key_signals: MISignal[];
  model_interpretation: string[];
  decision_view: MIDecisionView;
  summary: string;
  source: {
    ranking_engine: string;
    total_pairs: number;
    total_actionable: number;
  };
  selected_pair_view?: MISelectedPairView;
}

// ─── Hook ──────────────────────────────────────────────────────────

async function fetchMarketIntelligence(
  pair?: string
): Promise<MarketIntelligence> {
  const url = pair
    ? `${API_URL}/v1/market-intelligence?pair=${encodeURIComponent(pair)}`
    : `${API_URL}/v1/market-intelligence`;

  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Error ${response.status}: ${response.statusText}`);
  }
  return response.json();
}

export function useMarketIntelligence(
  pair?: string
): UseQueryResult<MarketIntelligence, Error> {
  return useQuery<MarketIntelligence, Error>({
    queryKey: ["market-intelligence", pair ?? "global"],
    queryFn: () => fetchMarketIntelligence(pair),
    staleTime: 5 * 60 * 1000,       // 5 min
    refetchInterval: 5 * 60 * 1000, // 5 min
  });
}
