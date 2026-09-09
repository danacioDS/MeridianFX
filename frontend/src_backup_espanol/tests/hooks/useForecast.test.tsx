/**
 * useForecast hook — infrastructure test.
 */
import type { ReactNode } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { useForecast } from "../../hooks/useForecast";
import { getForecast } from "../../services/forecast";
import type { ForecastResponse } from "../../types";

vi.mock("../../services/forecast", () => ({
  getForecast: vi.fn(),
}));

const mockedGetForecast = vi.mocked(getForecast);

const forecastFixture: ForecastResponse = {
  prediction_id: "pred-001",
  pair: "EURUSD",
  timestamp: "2026-08-27T00:00:00.000Z",
  as_of: "2026-08-27T00:00:00.000Z",
  delivery_state: "ELIGIBLE",
  delivery_reason: "Everything OK",
  delivery_warning: null,
  prediction: null,
  decision: null,
  data_quality: null,
  drivers: null,
  lineage: null,
};

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  };
}

describe("useForecast", () => {
  beforeEach(() => {
    mockedGetForecast.mockReset();
  });

  it("returns the raw backend response unchanged", async () => {
    mockedGetForecast.mockResolvedValueOnce(forecastFixture);

    const { result } = renderHook(() => useForecast("EURUSD"), {
      wrapper: createWrapper(),
    });

    // Esperar a que la query se resuelva
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    // Verificar que el dato es el esperado
    expect(result.current.data).toEqual(forecastFixture);
  });

  it("surfaces errors without transforming the response", async () => {
    const error = new Error("network failure");
    mockedGetForecast.mockRejectedValueOnce(error);

    const { result } = renderHook(() => useForecast("EURUSD"), {
      wrapper: createWrapper(),
    });

    await waitFor(() => {
      expect(result.current.error).toBeDefined();
    });

    expect(result.current.refetch).toBeTypeOf("function");
  });
});
