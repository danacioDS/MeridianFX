/**
 * Forecast service — infrastructure tests.
 *
 * Requirements:
 *  - Services do not transform responses (response === input).
 *  - Correct endpoint contract (path and generic payload type).
 *  - Nullability preserved (null fields are not substituted).
 */
import { beforeEach, describe, expect, it, vi } from "vitest";
import { apiClient } from "../../services/api";
import { getForecast } from "../../services/forecast";
import type { ForecastResponse } from "../../types";

vi.mock("../../services/api", () => ({
  apiClient: {
    get: vi.fn(),
  },
}));

const mockedGet = vi.mocked(apiClient.get);

const forecastFixture: ForecastResponse = {
  prediction_id: "pred-001",
  pair: "USDJPY",
  timestamp: "2026-08-27T00:00:00.000Z",
  as_of: "2026-08-27T00:00:00.000Z",
  delivery_state: "ELIGIBLE",
  delivery_reason: "Everything OK",
  delivery_warning: null,
  prediction: {
    direction: "NEUTRAL",
    probability: 0.5412,
    expected_return: 0.0012,
    expected_volatility: 0.0084,
    prediction_interval: { lower: -0.0053, upper: 0.0077 },
  },
  decision: {
    actionable: false,
    direction: "NEUTRAL",
    confidence: 0.51,
    signal_strength: "weak",
    edge_ratio: 1.02,
    net_return: 0.0004,
    position_size: 0,
  },
  data_quality: { overall: 0.94, status: "good" },
  drivers: null,
  lineage: null,
};

describe("getForecast", () => {
  beforeEach(() => {
    mockedGet.mockReset();
  });

  it("requests the Layer 1 forecast endpoint", async () => {
    mockedGet.mockResolvedValueOnce({ data: forecastFixture });
    await getForecast("USDJPY");
    expect(mockedGet).toHaveBeenCalledWith("/v1/fx/USDJPY/forecast");
  });

  it("returns the raw backend response without transformation (response === input)", async () => {
    mockedGet.mockResolvedValueOnce({ data: forecastFixture });
    const result = await getForecast("USDJPY");
    expect(result).toBe(forecastFixture);
  });

  it("preserves null fields instead of substituting defaults", async () => {
    const nullableFixture: ForecastResponse = {
      ...forecastFixture,
      prediction: null,
      decision: null,
      data_quality: null,
      delivery_state: "UNAVAILABLE",
    };
    mockedGet.mockResolvedValueOnce({ data: nullableFixture });
    const result = await getForecast("USDJPY");

    expect(result.delivery_state).toBe("UNAVAILABLE");
    expect(result.prediction).toBeNull();
    expect(result.decision).toBeNull();
    expect(result.data_quality).toBeNull();
  });
});