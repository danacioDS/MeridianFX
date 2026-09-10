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

// ─── Sub-contracts ─────────────────────────────────────────────────

export interface ShapValue {
  feature: string;
  value: number;
}

export interface MacroRegime {
  risk: string;
  policy: string;
  growth: string;
  inflation: string;
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

// ─── Top-level contract ────────────────────────────────────────────

export interface CanonicalDecision {
  pair: string;
  horizon_days: number;

  regime: string;

  macro_score: number | null;

  macro_data_status: MacroDataStatus;

  artifact: {
    macro_regime: MacroRegime;
    shap_values: ShapValue[];
    probability_up: number;
    expected_return: number;
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

  sizing?: SizingInfo | null;
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
