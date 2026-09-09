import { useQuery } from '@tanstack/react-query';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function fetchPrice(pair: string, period: string) {
  const response = await fetch(`${API_URL}/v1/fx/${pair}/price?period=${period}`);
  if (!response.ok) {
    throw new Error(`Error ${response.status}: ${response.statusText}`);
  }
  return response.json();
}

export function usePrice(pair: string, period: string = "1y") {
  return useQuery({
    queryKey: ['price', pair, period],
    queryFn: () => fetchPrice(pair, period),
    enabled: !!pair,
    refetchInterval: 60000, // Actualizar cada minuto
    staleTime: 30000,
  });
}
