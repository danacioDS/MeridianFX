/**
 * Status utilities — presentation-only mapping.
 * 
 * ALLOWED: mapping backend status values to display labels/colors.
 * FORBIDDEN: inferring status, calculating status, deriving status.
 */

export type StatusType = string | null | undefined;

export function getStatusColor(status: StatusType): string {
  if (!status) return "#8A8A9A";
  const normalized = String(status).toLowerCase();
  switch (normalized) {
    case "healthy":
    case "ok":
    case "valid":
    case "fresh":
    case "stable":
    case "none":
      return "#00D4AA";
    case "warning":
    case "degraded":
    case "stale":
    case "drift":
      return "#F5A623";
    case "error":
    case "unhealthy":
    case "invalid":
    case "failed":
      return "#FF6B6B";
    default:
      return "#8A8A9A";
  }
}

export function getStatusLabel(status: StatusType): string {
  if (!status) return "Unknown";
  const normalized = String(status).toLowerCase();
  switch (normalized) {
    case "healthy":
    case "ok":
      return "Healthy";
    case "warning":
    case "degraded":
      return "Degraded";
    case "error":
    case "unhealthy":
      return "Error";
    case "fresh":
      return "Fresh";
    case "stale":
      return "Stale";
    case "stable":
      return "Stable";
    case "drift":
      return "Drift Detected";
    case "valid":
      return "Valid";
    case "invalid":
      return "Invalid";
    case "none":
      return "None";
    default:
      return String(status);
  }
}

export function getSignalStrengthLabel(value: number | null | undefined): string {
  if (value === null || value === undefined) return "—";
  if (value >= 0.7) return "Strong";
  if (value >= 0.4) return "Moderate";
  return "Weak";
}

export function getDeliveryStateLabel(state: string | null | undefined): string {
  if (!state) return "—";
  const normalized = String(state).toLowerCase();
  switch (normalized) {
    case "eligible":
      return "Eligible";
    case "degraded":
      return "Degraded";
    case "unavailable":
      return "Unavailable";
    default:
      return String(state);
  }
}
