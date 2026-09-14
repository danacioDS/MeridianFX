import { useSearchParams } from "react-router-dom";
import { FX_PAIRS, DEFAULT_PAIR } from "../constants/fxPairs";
import type { RankingResponse } from "../types";

/**
 * MVP universe used when ranking data is unavailable.
 *
 * The full FX universe is defined in FX_PAIRS.
 * When ranking data is available, pairUniverseFromRanking()
 * uses the pairs returned by the ranking instead.
 */
export const DEFAULT_PAIR_UNIVERSE = [...FX_PAIRS];

/**
 * Returns the canonical pair universe.
 *
 * Historically this derived the universe from the ranking response, but
 * after the v2.7 registry promotion gate the legacy ranking collapsed to
 * a single pair (USD/CHF), which would have narrowed the entire UI to one
 * pair. The canonical decision/risk/narrative pipelines still cover all
 * 9 pairs, so the universe is now pinned to FX_PAIRS.
 *
 * The `ranking` argument is kept for backward compatibility but is no
 * longer used to define the universe.
 */
export function pairUniverseFromRanking(
  _ranking?: RankingResponse | null,
): string[] {
  return [...DEFAULT_PAIR_UNIVERSE];
}

interface ActivePair {
  pair: string;
  setPair: (next: string) => void;
}

export function useActivePair(): ActivePair {
  const [searchParams, setSearchParams] = useSearchParams();

  const pairParam = searchParams.get("pair");
  const isValid = pairParam ? FX_PAIRS.includes(pairParam as any) : false;
  const pair = isValid && pairParam ? pairParam : DEFAULT_PAIR;

  const setPair = (next: string) => {
    if (!FX_PAIRS.includes(next as any)) return;
    setSearchParams((prev) => {
      const params = new URLSearchParams(prev);
      params.set("pair", next);
      return params;
    });
  };

  return { pair, setPair };
}
