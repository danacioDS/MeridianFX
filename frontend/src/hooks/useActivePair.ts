import { useSearchParams } from "react-router-dom";
import type { RankingResponse } from "../types";

export const DEFAULT_PAIR = "USD/CNY";

// Todos los 9 pares disponibles
export const ALL_PAIRS: string[] = [
  "USD/JPY", "EUR/USD", "GBP/USD",
  "USD/CNY", "USD/MXN", "USD/BRL",
  "USD/ARS", "USD/BOB", "USD/CHF"
];

export const DEFAULT_PAIR_UNIVERSE: string[] = ALL_PAIRS;

export function pairUniverseFromRanking(ranking: RankingResponse | null | undefined): string[] {
  // Siempre devolver todos los pares
  return ALL_PAIRS;
}

interface ActivePair {
  pair: string;
  setPair: (next: string) => void;
}

export function useActivePair(): ActivePair {
  const [searchParams, setSearchParams] = useSearchParams();
  const pair = searchParams.get("pair") ?? DEFAULT_PAIR;

  const setPair = (next: string): void => {
    const params = new URLSearchParams(searchParams);
    params.set("pair", next);
    setSearchParams(params, { replace: false });
  };

  return { pair, setPair };
}
