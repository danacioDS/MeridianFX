import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../services/api';

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
  status: string;
  base: string;
  quote: string;
  base_available: boolean;
  quote_available: boolean;
  reason: string;
  policy_diff: string;
  growth_diff: string;
  rate_diff: string;
}

export interface CanonicalDecision {
  pair: string;
  horizon_days: number;
  regime: string;
  macro_score: number;
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
  };
  signals: {
    quant_score: { value: number };
    macro_score: { value: number };
    rag_score: { value: number };
  };
}

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
