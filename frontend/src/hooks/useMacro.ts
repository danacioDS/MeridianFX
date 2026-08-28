import { useQuery } from '@tanstack/react-query';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function fetchMacro() {
  const response = await fetch(`${API_URL}/v1/fx/macro/status`);
  if (!response.ok) {
    throw new Error(`Error ${response.status}: ${response.statusText}`);
  }
  return response.json();
}

async function fetchMacroContext() {
  const response = await fetch(`${API_URL}/v1/fx/interpretation?pair=USD/JPY&include_macro=true`);
  if (!response.ok) {
    throw new Error(`Error ${response.status}: ${response.statusText}`);
  }
  return response.json();
}

export function useMacroStatus() {
  return useQuery({
    queryKey: ['macro', 'status'],
    queryFn: fetchMacro,
    refetchInterval: 300000, // 5 minutos
    staleTime: 240000,
  });
}

export function useMacroContext() {
  return useQuery({
    queryKey: ['macro', 'context'],
    queryFn: fetchMacroContext,
    refetchInterval: 300000,
    staleTime: 240000,
  });
}
