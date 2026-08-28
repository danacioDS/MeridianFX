import { useQuery } from '@tanstack/react-query';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function fetchRanking() {
  const response = await fetch(`${API_URL}/v1/fx/ranking`);
  if (!response.ok) {
    throw new Error(`Error ${response.status}: ${response.statusText}`);
  }
  return response.json();
}

export function useRanking() {
  return useQuery({
    queryKey: ['ranking'],
    queryFn: fetchRanking,
    refetchInterval: 30000, // 30 segundos
  });
}
