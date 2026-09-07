import { useSearchParams } from "react-router-dom";
import { FX_PAIRS } from "../constants/fxPairs";

export const DEFAULT_PAIR = "EUR/USD";

/**
 * Universo canónico fijo.
 *
 * Se mantiene como array mutable para compatibilidad con
 * componentes y tests existentes.
 */
export const DEFAULT_PAIR_UNIVERSE: string[] = [...FX_PAIRS];

/**
 * Devuelve siempre el universo canónico.
 *
 * El argumento es opcional para mantener compatibilidad
 * con páginas legacy que todavía pasan ranking.data.
 */
export function pairUniverseFromRanking(_ranking?: unknown): string[] {
  return [...FX_PAIRS];
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

  return {
    pair,
    setPair,
  };
}
