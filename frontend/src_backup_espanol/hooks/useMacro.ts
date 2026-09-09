import { useQuery } from '@tanstack/react-query';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Función para obtener interpretación + macro para un par específico
export const fetchMacro = async (pair: string) => {
  const response = await fetch(`${API_URL}/v1/fx/interpretation?pair=${encodeURIComponent(pair)}&include_macro=true`);
  if (!response.ok) {
    throw new Error(`Error ${response.status}: ${response.statusText}`);
  }
  return response.json();
};

// Hook para usar el análisis macro de un par específico
export const useMacro = (pair: string) => {
  return useQuery({
    queryKey: ['macro', pair],
    queryFn: () => fetchMacro(pair),
    enabled: !!pair,
    refetchInterval: 300000, // 5 minutos
    staleTime: 240000, // 4 minutos
  });
};
