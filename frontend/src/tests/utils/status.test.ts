/**
 * Status utilities — infrastructure tests.
 *
 * Requirements:
 *  - Status mapping is one-to-one (every backend status string maps to a
 *    distinct label; no conflation).
 *  - Presentation only: unknown values fall through without interpretation.
 */
import { describe, expect, it } from "vitest";
import {
  DEFAULT_STATUS_COLOR,
  getDeliveryStateLabel,
  getSignalStrengthLabel,
  getStatusColor,
  getStatusLabel,
} from "../../utils/status";

const CONTRACT_STATUS_STRINGS = [
  "healthy",
  "degraded",
  "unhealthy",
  "failed",
  "good",
  "acceptable",
  "warning",
  "critical",
  "valid",
  "invalid",
  "ACTIVE",
  "DEGRADED",
  "SAFE_MODE",
  "HALTED",
  "ON",
  "OFF",
  "UNKNOWN",
  "ELIGIBLE",
  "NOT_ELIGIBLE",
  "UNAVAILABLE",
];

describe("getStatusLabel", () => {
  it("maps each contract status to a distinct label (one-to-one)", () => {
    const labels = CONTRACT_STATUS_STRINGS.map(getStatusLabel);
    expect(new Set(labels).size).toBe(labels.length);
    labels.forEach((label) => expect(label.length).toBeGreaterThan(0));
  });

  it("maps expected values", () => {
    expect(getStatusLabel("healthy")).toBe("Healthy");
    expect(getStatusLabel("ACTIVE")).toBe("Active");
    expect(getStatusLabel("SAFE_MODE")).toBe("Safe Mode");
    expect(getStatusLabel("HALTED")).toBe("Halted");
    expect(getStatusLabel("NOT_ELIGIBLE")).toBe("Not Eligible");
  });

  it("does not reinterpret unknown values (capitalization only)", () => {
    expect(getStatusLabel("some_unknown_state")).toBe("Some unknown state");
  });
});

describe("getStatusColor", () => {
  it("maps healthy statuses to the success color", () => {
    expect(getStatusColor("healthy")).toBe("#00D4AA");
    expect(getStatusColor("ACTIVE")).toBe("#00D4AA");
  });

  it("maps degraded statuses to the warning color", () => {
    expect(getStatusColor("degraded")).toBe("#F5A623");
    expect(getStatusColor("acceptable")).toBe("#F5A623");
  });

  it("maps unhealthy statuses to the error color", () => {
    expect(getStatusColor("unhealthy")).toBe("#FF6B6B");
    expect(getStatusColor("HALTED")).toBe("#FF6B6B");
    expect(getStatusColor("UNAVAILABLE")).toBe("#FF6B6B");
  });

  it("falls back to the neutral default without deriving status", () => {
    expect(getStatusColor("everything_is_fine")).toBe(DEFAULT_STATUS_COLOR);
  });
});

describe("getSignalStrengthLabel", () => {
  it("maps backend signal strength values to labels", () => {
    expect(getSignalStrengthLabel("weak")).toBe("Weak Signal");
    expect(getSignalStrengthLabel("moderate")).toBe("Moderate Signal");
    expect(getSignalStrengthLabel("strong")).toBe("Strong Signal");
  });
});

describe("getDeliveryStateLabel", () => {
  it("maps backend delivery state values to labels", () => {
    expect(getDeliveryStateLabel("ELIGIBLE")).toBe("Eligible");
    expect(getDeliveryStateLabel("NOT_ELIGIBLE")).toBe("Not Eligible");
    expect(getDeliveryStateLabel("UNAVAILABLE")).toBe("Unavailable");
  });
});