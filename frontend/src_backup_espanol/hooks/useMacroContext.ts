import { useQuery } from '@tanstack/react-query';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Función para obtener el contexto macro para un par específico
export const fetchMacroContext = async (pair: string) => {
  const response = await fetch(`${API_URL}/v1/fx/interpretation?pair=${encodeURIComponent(pair)}&include_macro=true`);
  if (!response.ok) {
    throw new Error(`Error ${response.status}: ${response.statusText}`);
  }
  return response.json();
};

// Hook para usar el contexto macro de un par específico
export const useMacroContext = (pair: string) => {
  return useQuery({
    queryKey: ['macro', 'context', pair],
    queryFn: () => fetchMacroContext(pair),
    enabled: !!pair,
    refetchInterval: 300000, // 5 minutos
    staleTime: 240000, // 4 minutos
  });
};
