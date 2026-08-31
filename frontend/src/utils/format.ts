/**
 * Formatting utilities for MeridianFX
 */

export const formatDateTime = (date: string | Date): string => {
  const d = typeof date === "string" ? new Date(date) : date;
  return d.toLocaleString("es-ES", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

export const formatPercent = (value: number): string => {
  if (value === undefined || value === null || !isFinite(value)) return "—";
  return `${(value * 100).toFixed(1)}%`;
};

export const formatNumber = (value: number, decimals: number = 2): string => {
  if (value === undefined || value === null || !isFinite(value)) return "—";
  return value.toFixed(decimals);
};

export const formatSharpe = (value: number): string => {
  if (value === undefined || value === null || !isFinite(value)) return "—";
  return value.toFixed(2);
};

export const formatDrawdown = (value: number): string => {
  if (value === undefined || value === null || !isFinite(value)) return "—";
  return `${(value * 100).toFixed(1)}%`;
};

export const formatEdgeRatio = (value: number): string => {
  if (value === undefined || value === null || !isFinite(value)) return "—";
  return value.toFixed(3);
};

export const formatProbability = (value: number): string => {
  if (value === undefined || value === null || !isFinite(value)) return "—";
  return `${(value * 100).toFixed(0)}%`;
};

export const formatDirection = (direction: string): string => {
  if (!direction) return "—";
  return direction === "UP" ? "Alcista" : direction === "DOWN" ? "Bajista" : direction;
};

export const getDirectionArrow = (direction: string): string => {
  if (!direction) return "—";
  return direction === "UP" ? "▲" : direction === "DOWN" ? "▼" : "—";
};

export const formatStatus = (status: string): string => {
  if (!status) return "—";
  const map: Record<string, string> = {
    healthy: "Operativo",
    degraded: "Degradado",
    critical: "Crítico",
    unknown: "Desconocido",
  };
  return map[status.toLowerCase()] || status;
};

export const formatEnum = (value: string): string => {
  if (!value) return "—";
  return value
    .toLowerCase()
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
};

export const formatCurrency = (value: number, currency: string = "USD"): string => {
  if (value === undefined || value === null || !isFinite(value)) return "—";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 4,
  }).format(value);
};

export const formatDate = (date: string | Date): string => {
  const d = typeof date === "string" ? new Date(date) : date;
  if (isNaN(d.getTime())) return "—";
  return d.toLocaleString("es-ES", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
};
