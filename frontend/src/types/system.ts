/**
 * System observability contracts — mirror of backend/layer1/routers/system.py
 *
 * These types describe the five /v1/system/* endpoints. They do NOT
 * compute any values; they only describe the shape returned by the
 * backend.
 */

export type LayerStatus = "HEALTHY" | "WARNING" | "DEGRADED" | "UNKNOWN";
export type CheckStatus = "OK" | "WARN" | "FAIL";
export type FinalVerdict = "ACTIONABLE" | "DEGRADED" | "UNAVAILABLE";

export interface SystemCheck {
  id: string;
  status: CheckStatus;
  finding?: string;
  detail: string;
}

export interface LayerEnvelope {
  layer: "data" | "research" | "decision" | "intelligence";
  status: LayerStatus;
  checks: SystemCheck[];
  findings: string[];
  summary?: Record<string, unknown>;
}

export interface DataLayer extends LayerEnvelope {
  layer: "data";
  pairs: Array<{
    pair: string;
    status: LayerStatus;
    base: { currency: string; series: string | null; semantic: string; status: string };
    quote: { currency: string; series: string | null; semantic: string; status: string };
    quote_provider: string | null;
    has_get_historical: boolean;
    has_get_context: boolean;
  }>;
  summary: {
    pairs_total: number;
    pairs_ok: number;
    pairs_mislabeled: number;
    pairs_absent: number;
    pairs_stale: number;
  };
}

export interface ResearchLayer extends LayerEnvelope {
  layer: "research";
  summary: {
    models_total: number;
    models_active: number;
    models_below_random: number;
    round_metrics: number;
    artifacts_missing_provenance: number;
    corpus_files: number;
    authoritative_registry: string;
  };
}

export interface DecisionLayer extends LayerEnvelope {
  layer: "decision";
  pair: string;
  decision: {
    direction: string | null;
    confidence: number | null;
    actionable: boolean | null;
    horizon_days: number | null;
    signal_validity: string | null;
  };
  economic: {
    net_return: number | null;
    edge_ratio: number | null;
    position_size: number | null;
    required_minimum_edge: number | null;
  };
  artifact: {
    model_id: string;
    model_version: string;
  };
}

export interface IntelligenceLayer extends LayerEnvelope {
  layer: "intelligence";
  sources: {
    server_legacy: { endpoint: string; total_pairs: number | null; total_actionable: number | null };
    canonical: { endpoint: string; total_pairs: number | null; total_actionable: number | null };
    client: { hook: string; loc: number | null };
  };
}

export interface SystemTrace {
  pair: string;
  final: FinalVerdict;
  findings: string[];
  layers: Record<string, { status: LayerStatus; findings: string[] }>;
  detail: {
    data: DataLayer;
    research: ResearchLayer;
    decision: DecisionLayer;
    intelligence: IntelligenceLayer;
  };
}
