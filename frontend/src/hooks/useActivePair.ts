/**
 * Active pair selection — composition (UI/Navigation) only.
 *
 * Reads/writes the `pair` search param so pair selection is shared across the
 * dashboard routes. Defaults to the mockup's primary pair. This is
 * presentation/navigation state — it never touches analytical data.
 */
import { useSearchParams } from "react-router-dom";
import type { RankingResponse } from "../types";

/** Default pair shown when no `pair` param is present (mockup primary). */
export const DEFAULT_PAIR = "USD/JPY";

/**
 * MVP currency universe (spec §MVP: 4 pairs).
 * Used only as a fallback list for navigation when the ranking stream is not
 * available yet; the authoritative universe comes from the ranking response.
 */
export const DEFAULT_PAIR_UNIVERSE: string[] = ["USD/JPY", "EUR/USD", "GBP/USD", "USD/CNY", "USD/MXN", "USD/BRL", "USD/ARS", "USD/BOB", "USD/CHF"];

/** Returns the pairs surfaced by the ranking stream, or the MVP fallback. */
export function pairUniverseFromRanking(ranking: RankingResponse | null | undefined): string[] {
  const pairs = ranking?.opportunities.map((opportunity) => opportunity.pair).filter(Boolean) ?? [];
  return pairs.length > 0 ? pairs : DEFAULT_PAIR_UNIVERSE;
}

interface ActivePair {
  /** Currently selected pair. */
  pair: string;
  /** Updates the `pair` search param (navigation only). */
  setPair: (next: string) => void;
}

/** Navigation-bound active pair. */
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