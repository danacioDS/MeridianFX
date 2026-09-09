import { useQuery } from '@tanstack/react-query';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function fetchForecastDashboard(pair: string) {
  const response = await fetch(`${API_URL}/v1/fx/${pair}/forecast-dashboard`);
  if (!response.ok) {
    throw new Error(`Error ${response.status}: ${response.statusText}`);
  }
  return response.json();
}

export function useForecastDashboard(pair: string) {
  return useQuery({
    queryKey: ['forecast-dashboard', pair],
    queryFn: () => fetchForecastDashboard(pair),
    enabled: !!pair,
    refetchInterval: 30000,
    staleTime: 15000,
  });
}
