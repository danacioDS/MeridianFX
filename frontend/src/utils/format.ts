/**
 * Utility functions for formatting values in the UI.
 * These are presentational only — no derivation or calculation.
 */

export function formatPercent(value: number | null | undefined): string {
  if (value == null) return "N/A";
  return `${(value * 100).toFixed(2)}%`;
}

export function formatProbability(value: number | null | undefined): string {
  if (value == null) return "N/A";
  return `${(value * 100).toFixed(2)}%`;
}

export function formatDateTime(value: string | null | undefined): string {
  if (!value) return "N/A";
  try {
    const date = new Date(value);
    if (isNaN(date.getTime())) return value;
    return date.toISOString().replace("T", " ").slice(0, 19);
  } catch {
    return value;
  }
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return "N/A";
  try {
    const date = new Date(value);
    if (isNaN(date.getTime())) return value;
    return date.toISOString().slice(0, 10);
  } catch {
    return value;
  }
}

export function formatNumber(value: number | null | undefined, decimals: number = 2): string {
  if (value == null) return "N/A";
  return value.toFixed(decimals);
}

export function formatDirection(value: string | null | undefined): string {
  if (!value) return "N/A";
  const map: Record<string, string> = {
    "LONG": "Long",
    "SHORT": "Short",
    "NEUTRAL": "Neutral",
    "UP": "Up",
    "DOWN": "Down",
  };
  return map[value.toUpperCase()] || value;
}

export function formatEdgeRatio(value: number | null | undefined): string {
  if (value == null) return "N/A";
  return `${value.toFixed(2)}x`;
}

export function formatSharpe(value: number | null | undefined): string {
  if (value == null) return "N/A";
  return value.toFixed(2);
}

export function formatDrawdown(value: number | null | undefined): string {
  if (value == null) return "N/A";
  return `${(value * 100).toFixed(2)}%`;
}

export function formatStatus(value: string | null | undefined): string {
  if (!value) return "N/A";
  const map: Record<string, string> = {
    "ACTIVE": "Active",
    "SAFE_MODE": "Safe Mode",
    "NOT_ELIGIBLE": "Not Eligible",
    "HEALTHY": "Healthy",
    "DEGRADED": "Degraded",
    "ERROR": "Error",
  };
  return map[value.toUpperCase()] || value;
}
