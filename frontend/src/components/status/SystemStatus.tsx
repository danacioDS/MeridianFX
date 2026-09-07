/**
 * System status panel — presentational only.
 *
 * Renders StatusResponse blocks verbatim: system_status, reason, timestamp,
 * intelligence (data quality, model health, decision validity, safe mode) and
 * Layer 4 metrics. No inference — every value is a backend field.
 */
import type { StatusResponse } from "../../types/contracts";
import { formatDateTime } from "../../utils";
import { getStatusColor, getStatusLabel } from "../../utils/status";
import { NotAvailable } from "../common/NotAvailable";

interface SystemStatusProps {
  /** Consolidated StatusResponse from /status. */
  status?: StatusResponse | null;
}

/**
 * Formatea un valor para mostrar en la UI.
 * Si es un objeto, extrae el campo 'status' o 'state' si existe.
 */
function formatValue(value: unknown): string {
  if (value === null || value === undefined) return "—";
  if (typeof value === 'string') return value;
  if (typeof value === 'number') return String(value);
  if (typeof value === 'boolean') return value ? '✅' : '❌';
  if (Array.isArray(value)) return `[${value.length} items]`;
  if (typeof value === 'object') {
    const obj = value as Record<string, unknown>;
    // Intentar extraer 'status' o 'state' del objeto
    if (obj.status) return String(obj.status);
    if (obj.state) return String(obj.state);
    if (obj.value) return String(obj.value);
    // Si tiene un campo 'message' o 'reason'
    if (obj.message) return String(obj.message);
    if (obj.reason) return String(obj.reason);
    // Si solo tiene un campo, mostrarlo
    const keys = Object.keys(obj);
    if (keys.length === 1) return String(obj[keys[0]]);
    // Fallback: mostrar keys principales
    return keys.slice(0, 3).map(k => `${k}: ${String(obj[k])}`).join(' · ');
  }
  return String(value);
}

export function SystemStatus({ status }: SystemStatusProps): JSX.Element {
  if (!status) {
    return (
      <NotAvailable
        feature="system-status"
        reason="UNSUPPORTED_BY_CONTRACT: StatusResponse payload absent"
      />
    );
  }

  const intelligence = status.intelligence;

  return (
    <div className="flex flex-col gap-4 rounded-lg border border-border bg-surface p-6">
      <div className="flex items-center gap-2">
        <span
          aria-hidden="true"
          className="inline-block h-2.5 w-2.5 rounded-full"
          style={{ backgroundColor: getStatusColor(status.system_status) }}
        />
        <span className="text-sm font-semibold text-text-primary">
          {getStatusLabel(status.system_status)}
        </span>
        {status.reason ? (
          <span className="text-xs text-text-secondary">{status.reason}</span>
        ) : null}
        <span className="ml-auto text-xs text-text-secondary">
          {formatDateTime(status.timestamp)}
        </span>
      </div>

      <dl className="grid grid-cols-2 gap-x-6 gap-y-3 text-sm">
        <Row label="Data Quality" value={intelligence.data_quality?.status ?? "—"} />
        <Row label="Overall Quality" value={intelligence.data_quality?.overall ?? "—"} />
        <Row label="Model Performance" value={intelligence.model_performance} />
        <Row label="Model Drift" value={intelligence.model_drift} />
        <Row label="Decision Validity" value={intelligence.decision_validity} />
        <Row label="Safe Mode" value={intelligence.safe_mode_state ?? "—"} />
        <Row label="Data Freshness" value={status.metrics?.data_freshness ?? "—"} />
        <Row 
          label="Coverage" 
          value={status.metrics?.prediction_coverage != null 
            ? `${(status.metrics.prediction_coverage * 100).toFixed(0)}%` 
            : "—"} 
        />
      </dl>
    </div>
  );
}

function Row({ label, value }: { label: string; value: unknown }): JSX.Element {
  const displayValue = formatValue(value);
  return (
    <div className="flex items-baseline justify-between gap-2">
      <dt className="text-xs text-text-secondary">{label}</dt>
      <dd className="text-sm font-medium text-text-primary">
        {displayValue}
      </dd>
    </div>
  );
}
