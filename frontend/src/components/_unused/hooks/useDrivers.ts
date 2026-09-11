import { useQuery } from '@tanstack/react-query';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function fetchDrivers(pair: string) {
  const response = await fetch(`${API_URL}/v1/fx/${pair}/drivers`);
  if (!response.ok) {
    throw new Error(`Error ${response.status}: ${response.statusText}`);
  }
  return response.json();
}

export function useDrivers(pair: string) {
  return useQuery({
    queryKey: ['drivers', pair],
    queryFn: () => fetchDrivers(pair),
    enabled: !!pair,
    refetchInterval: 30000,
  });
}
