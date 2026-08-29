import { useQuery } from "@tanstack/react-query";
import { getForecast } from "../services/forecast";

export function useForecast(pair: string) {
  return useQuery({
    queryKey: ["forecast", pair],
    queryFn: () => getForecast(pair),
    enabled: !!pair,
    refetchInterval: 30000,
    retry: 1,
  });
}
