/**
 * Contract gap helpers — infrastructure tests.
 *
 * Requirements:
 *  - Unsupported features return NOT_AVAILABLE.
 *  - NO_FALLBACK_ALLOWED is true.
 *  - NO_DERIVATION_ALLOWED is true.
 */
import { describe, expect, it } from "vitest";
import {
  CONTRACT_GAP_MAP,
  FEATURE_STATE,
  NO_DERIVATION_ALLOWED,
  NO_FALLBACK_ALLOWED,
} from "../../types/gaps";
import { getFeatureState, isUnsupported } from "../../utils/gaps";

describe("isUnsupported", () => {
  it("marks contract-gap features as unsupported", () => {
    expect(isUnsupported("getForecastHistory")).toBe(true);
    expect(isUnsupported("useForecastHistory")).toBe(true);
    expect(isUnsupported("getHealth")).toBe(true);
    expect(isUnsupported("position_size_recommendation")).toBe(true);
    expect(isUnsupported("regime")).toBe(true);
    expect(isUnsupported("economic_calendar")).toBe(true);
  });

  it("marks supported features as supported", () => {
    expect(isUnsupported("getForecast")).toBe(false);
    expect(isUnsupported("getRanking")).toBe(false);
    expect(isUnsupported("getDrivers")).toBe(false);
    expect(isUnsupported("getPerformance")).toBe(false);
    expect(isUnsupported("getStatus")).toBe(false);
  });
});

describe("getFeatureState", () => {
  it("returns NOT_AVAILABLE for unsupported features", () => {
    expect(getFeatureState("getForecastHistory")).toBe("NOT_AVAILABLE");
    expect(getFeatureState("position_size_recommendation")).toBe("NOT_AVAILABLE");
  });

  it("returns AVAILABLE for supported features", () => {
    expect(getFeatureState("getForecast")).toBe("AVAILABLE");
    expect(getFeatureState("getStatus")).toBe("AVAILABLE");
  });
});

describe("gap guards", () => {
  it("disallows fallback for all gaps", () => {
    expect(NO_FALLBACK_ALLOWED).toBe(true);
  });

  it("disallows derivation for all gaps", () => {
    expect(NO_DERIVATION_ALLOWED).toBe(true);
  });

  it("declares NOT_AVAILABLE for every register gap", () => {
    expect(FEATURE_STATE.NOT_AVAILABLE).toBe("NOT_AVAILABLE");
    Object.keys(CONTRACT_GAP_MAP).forEach((feature) => {
      expect(CONTRACT_GAP_MAP[feature]).toContain("UNSUPPORTED_BY_CONTRACT");
    });
  });
});