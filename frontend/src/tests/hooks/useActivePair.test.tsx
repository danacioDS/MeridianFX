/**
 * useActivePair / usePerformancePeriod — composition (navigation) tests.
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
  it("defaults to USD/CNY when no search param is present", () => {
    const { result } = setup(useActivePair);
    expect(result.current.pair).toBe("USD/CNY");
  });

  it("reads the pair from the search param", () => {
    const { result } = setup(useActivePair, ["/?pair=EUR/USD"]);
    expect(result.current.pair).toBe("EUR/USD");
  });

  it("writes the pair to the search param", () => {
    const { result } = setup(useActivePair);
    act(() => {
      result.current.setPair("USD/JPY");
    });
    expect(result.current.pair).toBe("USD/JPY");
  });

  it("ignores invalid pairs and falls back to default", () => {
    const { result } = setup(useActivePair, ["/?pair=INVALID/PAIR"]);
    expect(result.current.pair).toBe("USD/CNY");
  });
});

describe("usePerformancePeriod", () => {
  it("defaults to 6M when no period param is present", () => {
    const { result } = setup(usePerformancePeriod);
    expect(result.current.period).toBe("6M");
  });

  it("reads the period from the search param", () => {
    const { result } = setup(usePerformancePeriod, ["/?period=1Y"]);
    expect(result.current.period).toBe("1Y");
  });

  it("ignores periods outside the contract enum", () => {
    const { result } = setup(usePerformancePeriod, ["/?period=7D"]);
    expect(result.current.period).toBe("6M");
  });
});

describe("pairUniverseFromRanking", () => {
  it("falls back to the MVP universe when ranking is unavailable", () => {
    expect(pairUniverseFromRanking(null)).toEqual(DEFAULT_PAIR_UNIVERSE);
    expect(pairUniverseFromRanking(undefined)).toEqual(DEFAULT_PAIR_UNIVERSE);
  });

  it("returns all pairs from the ranking when available", () => {
    const ranking = {
      snapshot_timestamp: "2026-08-27T00:00:00Z",
      as_of: "2026-08-27T00:00:00Z",
      opportunities: [
        { rank: 1, pair: "EUR/USD", direction: "LONG", opportunity_score: 0.8, probability_up: 0.65, edge_ratio: 1.2, expected_return: 0.02, net_return: 0.015, position_size: 0.5, prediction_id: "p1", decision_id: "d1" },
        { rank: 2, pair: "GBP/USD", direction: "SHORT", opportunity_score: 0.6, probability_up: 0.35, edge_ratio: 1.0, expected_return: -0.01, net_return: -0.015, position_size: 0.3, prediction_id: "p2", decision_id: "d2" },
        { rank: 3, pair: "USD/JPY", direction: "LONG", opportunity_score: 0.5, probability_up: 0.55, edge_ratio: 0.8, expected_return: 0.01, net_return: 0.005, position_size: 0.2, prediction_id: "p3", decision_id: "d3" },
      ],
      top_opportunity: "EUR/USD",
      total_actionable: 1,
      total_pairs: 3,
    } satisfies RankingResponse;

    const result = pairUniverseFromRanking(ranking);
    expect(result).toEqual(["EUR/USD", "GBP/USD", "USD/JPY"]);
  });
});
