/**
 * Formatting utilities — infrastructure tests.
 *
 * Requirements:
 *  - Formatting functions preserve values (pure presentation).
 *  - No null replacement: null/undefined/NaN inputs are never substituted with
 *    a fabricated default (0, false, "", invented values).
 */
import { describe, expect, it } from "vitest";
import {
  formatCurrency,
  formatDate,
  formatDateTime,
  formatDirection,
  formatDrawdown,
  formatEdgeRatio,
  formatNumber,
  formatPercent,
  formatProbability,
  formatSharpe,
  formatStatus,
} from "../../utils/format";

describe("formatCurrency", () => {
  it("formats a positive value", () => {
    expect(formatCurrency(1234.5)).toBe("$1,234.50");
  });

  it("formats a negative value", () => {
    expect(formatCurrency(-12.34)).toBe("-$12.34");
  });

  it("does not replace null with a fabricated default", () => {
    const output = formatCurrency(null as unknown as number);
    expect(output).not.toBe("$0.00");
    expect(output).not.toBe("");
  });

  it("does not replace NaN with a fabricated default", () => {
    expect(formatCurrency(NaN)).not.toBe("$0.00");
  });
});

describe("formatPercent", () => {
  it("formats a 0-1 ratio as a percentage", () => {
    expect(formatPercent(0.1234)).toBe("12.34%");
  });

  it("does not replace null with 0%", () => {
    expect(formatPercent(null as unknown as number)).not.toBe("0%");
  });
});

describe("formatProbability", () => {
  it("formats a 0-1 probability as a percentage", () => {
    expect(formatProbability(0.8341)).toBe("83.41%");
  });
});

describe("formatDateTime", () => {
  it("formats an ISO datetime with date and time (UTC)", () => {
    expect(formatDateTime("2026-08-27T12:34:56.000Z")).toBe("2026-08-27 12:34:56");
  });

  it("preserves an unparseable value verbatim", () => {
    expect(formatDateTime("not-a-date")).toBe("not-a-date");
  });
});

describe("formatDate", () => {
  it("formats an ISO datetime with date only (UTC)", () => {
    expect(formatDate("2026-08-27T12:34:56.000Z")).toBe("2026-08-27");
  });
});

describe("formatNumber", () => {
  it("formats with the requested fixed decimals", () => {
    expect(formatNumber(1234.5678, 2)).toBe("1,234.57");
  });

  it("does not replace null with a rounded zero", () => {
    expect(formatNumber(null as unknown as number, 2)).not.toBe("0.00");
  });
});

describe("formatDirection", () => {
  it("maps direction codes to labels", () => {
    expect(formatDirection("LONG")).toBe("Long");
    expect(formatDirection("SHORT")).toBe("Short");
    expect(formatDirection("NEUTRAL")).toBe("Neutral");
    expect(formatDirection("BULLISH")).toBe("Bullish");
  });
});

describe("formatEdgeRatio", () => {
  it("formats an edge ratio with an x suffix", () => {
    expect(formatEdgeRatio(2.5)).toBe("2.5x");
  });

  it("does not fabricate a ratio for null", () => {
    expect(formatEdgeRatio(null as unknown as number)).not.toBe("0x");
  });
});

describe("formatSharpe", () => {
  it("formats with two decimals", () => {
    expect(formatSharpe(1.234)).toBe("1.23");
  });
});

describe("formatDrawdown", () => {
  it("formats a drawdown as a percentage", () => {
    expect(formatDrawdown(-0.1567)).toBe("-15.67%");
  });
});

describe("formatStatus", () => {
  it("maps status codes to labels", () => {
    expect(formatStatus("ACTIVE")).toBe("Active");
    expect(formatStatus("SAFE_MODE")).toBe("Safe Mode");
    expect(formatStatus("NOT_ELIGIBLE")).toBe("Not Eligible");
  });
});