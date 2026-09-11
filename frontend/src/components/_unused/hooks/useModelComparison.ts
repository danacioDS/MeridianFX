import { useQuery } from '@tanstack/react-query';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ModelMetrics {
  sharpe: number;
  profit_factor: number;
  da: number;
  auc: number;
  net_return: number;
  n_windows: number;
}

export interface ModelComparisonResponse {
  pair: string;
  horizon: number;
  initial_train_years: number;
  results: Record<string, ModelMetrics>;
  models: Record<string, { available: boolean }>;
  best_model: string | null;
  timestamp: string;
}

async function fetchModelComparison(
  pair: string,
  horizon: number = 5,
  initialTrainYears: number = 3
): Promise<ModelComparisonResponse> {
  const url =
    `${API_URL}/v1/fx/${pair}/model-comparison` +
    `?horizon=${horizon}&initial_train_years=${initialTrainYears}`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Error ${response.status}: ${response.statusText}`);
  }

  return response.json() as Promise<ModelComparisonResponse>;
}

export function useModelComparison(
  pair: string,
  horizon: number = 5,
  initialTrainYears: number = 3
) {
  return useQuery<ModelComparisonResponse>({
    queryKey: ['model-comparison', pair, horizon, initialTrainYears],
    queryFn: () => fetchModelComparison(pair, horizon, initialTrainYears),
    enabled: !!pair,
    refetchInterval: 60000,
    staleTime: 30000,
  });
}
