import { useQuery } from '@tanstack/react-query';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function fetchForecast(pair: string) {
  console.log('[useForecast] Pair recibido:', pair);
  
  // Si el par ya incluye USD/, no lo dupliques
  let base, quote;
  if (pair.startsWith('USD/')) {
    // El par ya tiene formato completo: USD/BOB
    const parts = pair.split('/');
    base = parts[0];
    quote = parts[1];
  } else {
    // Si no, dividir normalmente
    const parts = pair.split('/');
    base = parts[0] || 'USD';
    quote = parts[1] || pair;
  }
  
  const url = `${API_URL}/v1/fx/${base}/${quote}/forecast`;
  
  console.log(`[useForecast] Fetching: ${url}`);
  
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Error ${response.status}: ${response.statusText}`);
  }
  return response.json();
}

export function useForecast(pair: string) {
  return useQuery({
    queryKey: ['forecast', pair],
    queryFn: () => fetchForecast(pair),
    enabled: !!pair && pair.includes('/'),
    refetchInterval: 30000,
    retry: 1,
  });
}
