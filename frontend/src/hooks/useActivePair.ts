import { useSearchParams } from "react-router-dom";
import { FX_PAIRS } from "../constants/fxPairs";

export const DEFAULT_PAIR = "EUR/USD";

export function pairUniverseFromRanking(): string[] {
  // Siempre devolver el orden fijo, no depender del ranking
  return FX_PAIRS;
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
