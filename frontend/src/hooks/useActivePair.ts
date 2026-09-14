import { useSearchParams } from "react-router-dom";
import { FX_PAIRS, DEFAULT_PAIR } from "../constants/fxPairs";
import type { RankingResponse } from "../types";

export const CANONICAL_FX_PAIRS = [...FX_PAIRS];

export function pairUniverseFromRanking(_ranking?: RankingResponse | null): string[] {
  return [...CANONICAL_FX_PAIRS];
}

interface ActivePair {
  pair: string;
  setPair: (next: string) => void;
  availablePairs: string[];
}

export function useActivePair(rankingPairs: string[] = []): ActivePair {
  const [searchParams, setSearchParams] = useSearchParams();

  const pairParam = searchParams.get("pair");
  const isValid = pairParam ? CANONICAL_FX_PAIRS.includes(pairParam as any) : false;
  const pair = isValid && pairParam ? pairParam : DEFAULT_PAIR;

  const availablePairs = rankingPairs.length > 0
    ? Array.from(new Set([...rankingPairs, ...CANONICAL_FX_PAIRS]))
    : CANONICAL_FX_PAIRS;

  const setPair = (next: string) => {
    if (!CANONICAL_FX_PAIRS.includes(next as any)) return;
    setSearchParams((prev) => {
      const params = new URLSearchParams(prev);
      params.set("pair", next);
      return params;
    });
  };

  return { pair, setPair, availablePairs };
}
