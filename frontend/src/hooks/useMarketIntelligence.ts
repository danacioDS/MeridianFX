/**
 * useMarketIntelligence — Market Intelligence aggregate for Global.
 *
 * Consumes: GET /v1/fx/ranking  (canonical pipeline)
 *
 * ⚠️  This hook is PURE TRANSPORT. Types are declared locally; no
 *     calculation, no aggregation, no derivation is performed.
 *
 * History:
 *   - Before: consumed /v1/market-intelligence (legacy RankingEngine,
 *     USD/CHF-only, returned 0 pairs in production after the promotion gate).
 *   - Now: consumes /v1/fx/ranking (canonical PipelineBridge, 9 pairs,
 *     Logistic_24 + KI-009). The legacy endpoint is deprecated at the
 *     frontend level until the backend migration lands.
 */
import { useQuery, type UseQueryResult } from "@tanstack/react-query";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// ─── Types (mirror backend v2.3.0+) ────────────────────────────────

export interface MISignal {
  pair: string;
  direction: string;         // "bullish" | "bearish" | "neutral"
  confidence: number;        // [0, 1]
  edge_ratio: number;
  opportunity_score: number;
  actionable: boolean;
}

export interface MIDecisionView {
  status: string;            // "ACTIONABLE" | "SELECTIVE"
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

// ─── Canonical ranking → MarketIntelligence adapter ────────────────

interface CanonicalOpportunity {
  rank: number;
  pair: string;
  direction: string;         // "UP" | "DOWN" | "NEUTRAL"
  opportunity_score: number;
  edge_ratio: number;
  actionable: boolean;
  confidence: number;
  decision_quality: string;  // "HIGH" | "MEDIUM" | "LOW"
  position_size: number;
}

interface CanonicalRanking {
  timestamp: string;
  opportunities: CanonicalOpportunity[];
  top_opportunity: CanonicalOpportunity | null;
  total_actionable: number;
  total_pairs: number;
}

function _directionLabel(direction: string): string {
  if (direction === "UP") return "bullish";
  if (direction === "DOWN") return "bearish";
  return "neutral";
}

function _buildContext(
  opportunities: CanonicalOpportunity[],
  actionable: CanonicalOpportunity[]
): MICurrentContext {
  const context =
    actionable.length > 0
      ? `The decision layer has identified ${actionable.length} actionable ` +
        `opportunit${actionable.length > 1 ? "ies" : "y"} across the monitored ` +
        `FX universe. An actionable signal means: the model has a directional ` +
        `view, the expected return after costs (net return) is large enough to ` +
        `exceed the required minimum edge, and all hard gates have passed.`
      : "The MeridianFX decision layer is currently SELECTIVE. This means " +
        "the system has evaluated every pair in the monitored universe and " +
        "found that none currently satisfies the full set of economic criteria " +
        "required for an actionable signal. In practical terms: a model may " +
        "have a directional view, but the expected profit after transaction " +
        "costs is not large enough, relative to the required minimum edge, to " +
        "justify exposure. The system therefore prefers no position over a " +
        "marginal one.";

  return {
    market_coverage: opportunities.length,
    actionable_opportunities: actionable.length,
    context,
  };
}

function _buildSignals(
  opportunities: CanonicalOpportunity[],
  selectedPair?: string
): MISignal[] {
  // Si hay un par seleccionado, lo ponemos primero
  let ordered = opportunities;
  if (selectedPair) {
    const selected = opportunities.find((o) => o.pair === selectedPair);
    if (selected) {
      ordered = [
        selected,
        ...opportunities.filter((o) => o.pair !== selectedPair),
      ];
    }
  }

  return ordered.slice(0, 5).map((o) => ({
    pair: o.pair,
    direction: _directionLabel(o.direction),
    confidence: Math.round(o.confidence * 10000) / 10000,
    edge_ratio: Math.round(o.edge_ratio * 10000) / 10000,
    opportunity_score: Math.round(o.opportunity_score * 10000) / 10000,
    actionable: o.actionable,
  }));
}

function _buildInterpretation(
  opportunities: CanonicalOpportunity[],
  selectedPair?: string
): string[] {
  if (opportunities.length === 0) {
    return [
      "No model-ranked opportunities are currently available.",
      "The intelligence layer cannot establish a directional market view " +
        "without valid research outputs.",
    ];
  }

  const selected = selectedPair
    ? opportunities.find((o) => o.pair === selectedPair)
    : undefined;

  if (selectedPair && !selected) {
    return [
      `${selectedPair} is not part of the monitored ranking universe.`,
      "The ranking currently tracks only pairs that passed the registry " +
        "promotion gate. The canonical Decision pipeline still evaluates " +
        "this pair separately.",
    ];
  }

  const top = selected ?? opportunities[0];
  const direction = _directionLabel(top.direction);
  const confidencePct = (top.confidence * 100).toFixed(1);
  const edge = top.edge_ratio.toFixed(2);

  const interpretation = [
    `${top.pair} is classified as ${
      top.actionable ? "ACTIONABLE" : "NOT ACTIONABLE"
    }.`,
    `Direction: ${direction}, confidence ${confidencePct}%, quality ${top.decision_quality}.`,
    `Edge: ${edge}x.`,
  ];

  if (top.actionable) {
    interpretation.push(
      "The signal passes the economic filter and warrants further " +
        "evaluation for exposure."
    );
  } else {
    interpretation.push(
      "The signal does not exceed the economic threshold. The rest of the " +
        "universe remains SELECTIVE."
    );
  }

  if (top.rank != null) {
    interpretation.push(
      `Ranking: position #${top.rank} of ${opportunities.length} monitored pairs.`
    );
  }

  return interpretation;
}

function _buildSummary(
  opportunities: CanonicalOpportunity[],
  actionable: CanonicalOpportunity[],
  selectedPair?: string
): string {
  if (opportunities.length === 0) {
    return (
      "MeridianFX currently has insufficient ranked research signals to " +
      "produce a reliable market-intelligence view."
    );
  }

  const selected = selectedPair
    ? opportunities.find((o) => o.pair === selectedPair)
    : undefined;

  if (selectedPair && !selected) {
    return (
      `${selectedPair} is not part of the monitored ranking universe. ` +
      `The ranking currently tracks only pairs that passed the registry ` +
      `promotion gate. See the Decision page for the canonical evaluation ` +
      `of this pair.`
    );
  }

  const top = selected ?? opportunities[0];
  const direction = _directionLabel(top.direction);
  const confidencePct = (top.confidence * 100).toFixed(1);
  const edge = top.edge_ratio.toFixed(2);

  if (top.actionable) {
    return (
      `${top.pair} passes the economic filter with direction ${direction}, ` +
      `confidence ${confidencePct}%, and edge ${edge}x. It warrants further ` +
      `evaluation for exposure.`
    );
  }

  return (
    `${top.pair} is not actionable. Direction: ${direction}, confidence ` +
    `${confidencePct}%, edge ${edge}x. The rest of the universe remains SELECTIVE.`
  );
}

function _buildSelectedPairView(
  opportunities: CanonicalOpportunity[],
  pair: string
): MISelectedPairView | undefined {
  const selected = opportunities.find((o) => o.pair === pair);

  if (!selected) {
    return {
      pair,
      available: false,
      reason: "PAIR_NOT_IN_RANKING",
      narrative:
        `${pair} is not part of the monitored ranking universe. ` +
        `The canonical Decision pipeline still evaluates this pair separately.`,
    };
  }

  const directionLabel = _directionLabel(selected.direction);
  const confidencePct = (selected.confidence * 100).toFixed(1);
  const edge = selected.edge_ratio.toFixed(2);

  let status: MISelectedPairView["status"];
  let narrative: string;

  if (selected.actionable) {
    status = "ACTIONABLE";
    narrative =
      `${pair} passes the economic filter. Direction: ${directionLabel}, ` +
      `confidence ${confidencePct}%, edge ${edge}x.`;
  } else {
    status = "NOT_ACTIONABLE";
    narrative =
      `${pair} is not actionable. Edge ${edge}x is below the threshold. ` +
      `The rest of the universe remains SELECTIVE.`;
  }

  return {
    pair,
    available: true,
    status,
    rank: selected.rank,
    direction: selected.direction,
    direction_label: directionLabel,
    confidence: Math.round(selected.confidence * 10000) / 10000,
    edge_ratio: Math.round(selected.edge_ratio * 10000) / 10000,
    opportunity_score: Math.round(selected.opportunity_score * 10000) / 10000,
    quality: selected.decision_quality,
    actionable: selected.actionable,
    narrative,
  };
}

function _adaptCanonicalRanking(
  ranking: CanonicalRanking,
  pair?: string
): MarketIntelligence {
  const opportunities = ranking.opportunities ?? [];
  const actionable = opportunities.filter((o) => o.actionable);

  const decisionView: MIDecisionView = {
    status: actionable.length > 0 ? "ACTIONABLE" : "SELECTIVE",
    actionable_count: actionable.length,
    total_pairs: opportunities.length,
    principle:
      "Prediction is not equivalent to a trading decision. MeridianFX " +
      "requires economic edge and decision validity before classifying a " +
      "signal as actionable.",
  };

  const result: MarketIntelligence = {
    timestamp: ranking.timestamp ?? new Date().toISOString(),
    system: "MeridianFX",
    language: "en",
    architecture: {
      data: "market and macroeconomic observations",
      research: "model forecasts and ranked opportunities",
      decision: "economic edge and actionability",
      intelligence: "contextual synthesis",
    },
    current_context: _buildContext(opportunities, actionable),
    key_signals: _buildSignals(opportunities, pair),
    model_interpretation: _buildInterpretation(opportunities, pair),
    decision_view: decisionView,
    summary: _buildSummary(opportunities, actionable, pair),
    source: {
      ranking_engine:
        "backend.layer1.routers.ranking.evaluate_canonical_universe",
      total_pairs: opportunities.length,
      total_actionable: actionable.length,
    },
  };

  if (pair) {
    const view = _buildSelectedPairView(opportunities, pair);
    if (view) {
      result.selected_pair_view = view;
    }
  }

  return result;
}

// ─── Hook ──────────────────────────────────────────────────────────

async function fetchMarketIntelligence(
  pair?: string
): Promise<MarketIntelligence> {
  // Consume the canonical ranking endpoint (9 pairs, PipelineBridge).
  // The legacy /v1/market-intelligence endpoint is deprecated at the
  // frontend level until the backend migration lands.
  const response = await fetch(`${API_URL}/v1/fx/ranking`);
  if (!response.ok) {
    throw new Error(`Error ${response.status}: ${response.statusText}`);
  }
  const ranking: CanonicalRanking = await response.json();
  return _adaptCanonicalRanking(ranking, pair);
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
