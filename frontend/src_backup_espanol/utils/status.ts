// src/utils/status.ts

export const DEFAULT_STATUS_COLOR = "#6B7280";

export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    healthy: "#00D4AA",
    ACTIVE: "#00D4AA",
    degraded: "#F5A623",
    acceptable: "#F5A623",
    unhealthy: "#FF6B6B",
    HALTED: "#FF6B6B",
    UNAVAILABLE: "#FF6B6B",
  };
  return colors[status] ?? DEFAULT_STATUS_COLOR;
}

export function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    healthy: "Healthy",
    degraded: "Degraded",
    unhealthy: "Unhealthy",
    failed: "Failed",
    good: "Good",
    acceptable: "Acceptable",
    warning: "Warning",
    critical: "Critical",
    valid: "Valid",
    invalid: "Invalid",
    ACTIVE: "Active",
    DEGRADED: "Degraded (Active)",
    SAFE_MODE: "Safe Mode",
    HALTED: "Halted",
    ON: "On",
    OFF: "Off",
    UNKNOWN: "Unknown",
    ELIGIBLE: "Eligible",
    NOT_ELIGIBLE: "Not Eligible",
    UNAVAILABLE: "Unavailable",
  };

  if (labels[status]) {
    return labels[status];
  }

  return status
    .replace(/_/g, " ")
    .toLowerCase()
    .replace(/^\w/, (c) => c.toUpperCase());
}

export function getDeliveryStateLabel(state: string): string {
  const labels: Record<string, string> = {
    ELIGIBLE: "Eligible",
    NOT_ELIGIBLE: "Not Eligible",
    UNAVAILABLE: "Unavailable",
  };
  return labels[state] ?? state;
}

export function getSignalStrengthLabel(value: number | string): string {
  // Si es string, verificar si es un SignalStrength del contrato
  if (typeof value === "string") {
    const map: Record<string, string> = {
      weak: "Weak Signal",
      moderate: "Moderate Signal",
      strong: "Strong Signal",
      HIGH: "Alta",
      MEDIUM: "Media",
      LOW: "Baja",
    };
    return map[value.toLowerCase()] ?? value;
  }

  // Si es número
  if (value >= 0.7) return "Strong Signal";
  if (value >= 0.4) return "Moderate Signal";
  return "Weak Signal";
}
