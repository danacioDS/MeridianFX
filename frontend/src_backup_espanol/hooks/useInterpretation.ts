import { useQuery } from '@tanstack/react-query';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function fetchInterpretation(pair: string) {
  const response = await fetch(`${API_URL}/v1/fx/interpretation?pair=${encodeURIComponent(pair)}`);
  if (!response.ok) {
    throw new Error(`Error ${response.status}: ${response.statusText}`);
  }
  return response.json();
}

export function useInterpretation(pair: string) {
  return useQuery({
    queryKey: ['interpretation', pair],
    queryFn: () => fetchInterpretation(pair),
    enabled: !!pair,
    staleTime: 60000,
    refetchInterval: 120000,
  });
}
