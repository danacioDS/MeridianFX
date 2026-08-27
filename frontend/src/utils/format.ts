/**
 * Presentation-only formatting utilities.
 *
 * MUST be pure formatting functions: they only re-format a value given by the
 * backend. MUST NOT calculate, infer, derive, or substitute analytical values.
 * MUST NOT replace null/undefined/NaN with a fabricated default (0, false, "",
 * or invented values): if the input is not a finite number it is preserved by
 * returning its string representation unchanged.
 */
import { format as formatDateFns } from "date-fns";

function finiteNumber(value: number): number | null {
  if (value == null) return null;
  if (typeof value !== "number") return null;
  if (Number.isNaN(value) || !Number.isFinite(value)) return null;
  return value;
}

function parseDate(value: string): Date | null {
  if (value == null) return null;
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date;
}

/** Title-cases a backend code string (presentation only). */
function toTitleCase(value: string): string {
  return value
    .toLowerCase()
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

/** Formats a value as USD currency. */
export function formatCurrency(value: number): string {
  const n = finiteNumber(value);
  if (n == null) return String(value);
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(n);
}

/** Formats a 0–1 ratio as a percentage. */
export function formatPercent(value: number): string {
  const n = finiteNumber(value);
  if (n == null) return String(value);
  return new Intl.NumberFormat("en-US", { style: "percent", maximumFractionDigits: 2 }).format(n);
}

/** Formats a probability (0–1) as a percentage. */
export function formatProbability(value: number): string {
  return formatPercent(value);
}

/** Formats an ISO datetime string with date and time. */
export function formatDateTime(value: string): string {
  const date = parseDate(value);
  if (date == null) return String(value);
  return formatDateFns(date, "yyyy-MM-dd HH:mm:ss");
}

/** Formats an ISO datetime string with date only. */
export function formatDate(value: string): string {
  const date = parseDate(value);
  if (date == null) return String(value);
  return formatDateFns(date, "yyyy-MM-dd");
}

/** Formats a number with a fixed number of decimals. */
export function formatNumber(value: number, decimals: number): string {
  const n = finiteNumber(value);
  if (n == null) return String(value);
  return new Intl.NumberFormat("en-US", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(n);
}

/** Formats a direction code (BULLISH/BEARISH/NEUTRAL/LONG/SHORT) with capitalization. */
export function formatDirection(value: string): string {
  if (value == null) return String(value);
  return toTitleCase(value);
}

/** Formats an edge ratio with an x suffix. */
export function formatEdgeRatio(value: number): string {
  const n = finiteNumber(value);
  if (n == null) return String(value);
  return `${new Intl.NumberFormat("en-US", { maximumFractionDigits: 2 }).format(n)}x`;
}

/** Formats a Sharpe ratio with fixed decimals. */
export function formatSharpe(value: number): string {
  return formatNumber(value, 2);
}

/** Formats a drawdown value as a percentage. */
export function formatDrawdown(value: number): string {
  const n = finiteNumber(value);
  if (n == null) return String(value);
  return formatPercent(n);
}

/** Formats a backend status code with title-case. */
export function formatStatus(value: string): string {
  if (value == null) return String(value);
  return toTitleCase(value);
}

/** Maps a direction enum to a display arrow glyph (presentation only). */
export function getDirectionArrow(value: string): string {
  if (value == null) return String(value);
  switch (value) {
    case "BULLISH":
    case "LONG":
      return "▲";
    case "BEARISH":
    case "SHORT":
      return "▼";
    default:
      return "◆";
  }
}