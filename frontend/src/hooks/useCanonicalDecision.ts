/**
 * useCanonicalDecision — Canonical Decision hook.
 *
 * Consumes: GET /v1/canonical/{pair}/decision?horizon_days={h}
 *
 * ⚠️  This hook is PURE TRANSPORT + TYPING.
 *     It does NOT compute any analytical values.
 *
 * ⚠️  Types reflect the v2.3.0 canonical contract.
 *     Many fields are nullable (macro_score, sizing, reason) when the
 *     model is unavailable or the macro data is partial.
 */
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../services/api';
import type { MacroRegime } from '../types/contracts';

// ─── Sub-contracts ─────────────────────────────────────────────────

export interface ShapValue {
  feature: string;
  value: number;
}

export interface MacroDataStatus {
  base: string;
  quote: string;
  policy_differential: number | null;
  growth_differential: number | null;
  inflation_differential: number | null;
  base_rate: number | null;
  quote_rate: number | null;
  status: string;               // FULL | PARTIAL | UNAVAILABLE
  base_available: boolean;
  quote_available: boolean;
  reason: string | null;
}

export interface SizingMultipliers {
  edge: number;
  quality: number;
  volatility: number;
}

export interface SizingInfo {
  position_size: number;
  base_size: number;
  available_capacity: number;
  multipliers: SizingMultipliers;
  rejection_reason: string | null;
  capacity_constrained: boolean;
}


// ─── Gate ──────────────────────────────────────────────────────────

export interface GateInfo {
  gate_results: Record<string, boolean>;
  all_passed: boolean;
  first_failing_gate: string | null;
  thresholds_used: Record<string, number>;
  signal_validity: string;
  rejection_reason: string | null;
  degraded_warnings: string[];
}

// ─── Costs ─────────────────────────────────────────────────────────

export interface CostsInfo {
  spread: number;
  slippage: number;
  commission: number;
  total_cost: number;
  normalized_volatility: number;
  vix: number;
}

// ─── Economic ──────────────────────────────────────────────────────

export interface EconomicInfo {
  directional_gross_return: number;
  carry_proxy: number;
  total_cost: number;
  net_return: number;
  edge_ratio: number;
  required_minimum_edge: number;
  actionable: boolean;
}

// ─── Quality ───────────────────────────────────────────────────────

export interface QualityComponents {
  confidence: number;
  freshness: number;
  regime_alignment: number;
  data_quality: string;
  data_quality_score: number;
  drift_score: number;
}

export interface QualityInfo {
  score: number;
  components: QualityComponents;
  level: string;
  fallback_status: Record<string, string>;
}

// ─── Fusion ────────────────────────────────────────────────────────

export interface FusionWeights {
  quant: number;
  macro: number;
  rag: number;
}

export interface FusionInfo {
  regime: string;
  weights: FusionWeights;
  fusion_score: number;
  direction: string;
  direction_sign: number;
  confidence: number | null;
}

// ─── Risk (resumen) ────────────────────────────────────────────────

export interface RiskSummaryDriver {
  name: string;
  contribution: number;
  normalized_value: number;
  weight: number;
  explanation: string;
}

export interface RiskSummary {
  risk_score: number;
  risk_level: string;
  drivers: RiskSummaryDriver[];
  methodology_version: string;
}

// ─── Top-level contract ────────────────────────────────────────────

export interface CanonicalDecision {
  pair: string;
  horizon_days: number;

  regime: string;
  vix: number;

  macro_score: number | null;

  macro_data_status: MacroDataStatus;

  artifact: {
    macro_regime: MacroRegime;
    shap_values: ShapValue[];
    probability_up: number;
    expected_return: number;
    expected_volatility: number;
    confidence_interval: {
      lower: number;
      upper: number;
    };
  };

  decision: {
    direction: string;
    confidence: number;
    actionable: boolean;
    rejection_reason: string | null;
    edge_ratio: number;
    net_return: number;
    position_size: number;
    signal_validity: string;
  };

  signals: {
    quant_score: { value: number };
    macro_score: { value: number } | null;
    rag_score: { value: number };
  };

  gate: GateInfo;
  sizing?: SizingInfo | null;
  fusion: FusionInfo;
  costs: CostsInfo;
  economic: EconomicInfo;
  quality: QualityInfo;
  risk: RiskSummary;
}

// ─── Hook ──────────────────────────────────────────────────────────

export function useCanonicalDecision(pair: string, horizonDays: number = 30) {
  const url = `/v1/canonical/${pair}/decision?horizon_days=${horizonDays}`;

  return useQuery<CanonicalDecision>({
    queryKey: ['canonical', pair, horizonDays],
    queryFn: async () => {
      const response = await apiClient.get(url);
      return response.data;
    },
    enabled: !!pair,
    staleTime: 5 * 60 * 1000,
  });
}
