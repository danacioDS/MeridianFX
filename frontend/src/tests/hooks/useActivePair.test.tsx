/**
 * useActivePair / usePerformancePeriod — composition (navigation) tests.
 *
 * Requirements:
 *  - Pair defaults to USD/JPY and reads/writes the `pair` search param.
 *  - Period defaults to 6M and rejects values outside the contract enum.
 *  - pairUniverseFromRanking uses ranking pairs, falling back to the MVP list.
 */
import type { ReactNode } from "react";
import { MemoryRouter, type MemoryRouterProps } from "react-router-dom";
import { renderHook, act } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import {
  DEFAULT_PAIR,
  DEFAULT_PAIR_UNIVERSE,
  pairUniverseFromRanking,
  useActivePair,
} from "../../hooks/useActivePair";
import { usePerformancePeriod } from "../../hooks/usePerformancePeriod";
import type { RankingResponse } from "../../types";

function RouterWrapper({ children, initialEntries }: Pick<MemoryRouterProps, "children" | "initialEntries">) {
  return <MemoryRouter initialEntries={initialEntries ?? ["/"]}>{children}</MemoryRouter>;
}

function setup<T>(hook: () => T, initialEntries?: string[]) {
  return renderHook(hook, {
    wrapper: ({ children }: { children: ReactNode }) => (
      <RouterWrapper initialEntries={initialEntries}>{children}</RouterWrapper>
    ),
  });
}

describe("useActivePair", () => {
  it("defaults to USD/JPY when the pair param is absent", () => {
    const { result } = setup(useActivePair);
    expect(result.current.pair).toBe(DEFAULT_PAIR);
  });

  it("reads the pair from the search param", () => {
    const { result } = setup(useActivePair, ["/?pair=EUR%2FUSD"]);
    expect(result.current.pair).toBe("EUR/USD");
  });

  it("writes the pair back to the search params", () => {
    const { result } = setup(useActivePair);
    act(() => result.current.setPair("GBP/USD"));
    expect(result.current.pair).toBe("GBP/USD");
  });
});

describe("usePerformancePeriod", () => {
  it("defaults to 6M", () => {
    const { result } = setup(usePerformancePeriod);
    expect(result.current.period).toBe("6M");
  });

  it("reads a valid period from the search param", () => {
    const { result } = setup(usePerformancePeriod, ["/?period=1Y"]);
    expect(result.current.period).toBe("1Y");
  });

  it("ignores periods outside the contract enum", () => {
    const { result } = setup(usePerformancePeriod, ["/?period=7D"]);
    expect(result.current.period).toBe("6M");
  });
});

describe("pairUniverseFromRanking", () => {
  it("uses ranking pairs when present", () => {
    const ranking = {
      snapshot_timestamp: "2026-08-27T00:00:00Z",
      as_of: "2026-08-27T00:00:00Z",
      opportunities: [
        {
          rank: 1,
          pair: "EUR/USD",
          direction: "LONG",
          opportunity_score: 0.8,
          edge_ratio: 2.0,
          actionable: true,
          confidence: 0.9,
          decision_quality: 0.7,
          position_size: 0.5,
          prediction_id: "p1",
          decision_id: "d1",
        },
      ],
      top_opportunity: "EUR/USD",
      total_actionable: 1,
      total_pairs: 1,
    } satisfies RankingResponse;

    expect(pairUniverseFromRanking(ranking)).toEqual(["EUR/USD"]);
  });

  it("falls back to the MVP universe when ranking is unavailable", () => {
    expect(pairUniverseFromRanking(null)).toEqual(DEFAULT_PAIR_UNIVERSE);
    expect(pairUniverseFromRanking(undefined)).toEqual(DEFAULT_PAIR_UNIVERSE);
  });
});