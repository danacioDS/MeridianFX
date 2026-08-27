/**
 * Header — presentational only.
 *
 * Mockup topbar: brand + page title, data freshness line, and a status
 * indicator. Receives status + timestamp via props (no hooks). The visual
 * status dot maps an existing backend status string to a color via
 * getStatusColor — it never infers freshness or coverage.
 */
import { formatDateTime } from "../../utils";
import { getStatusColor, getStatusLabel } from "../../utils/status";

interface HeaderProps {
  /** Page title (mockup topbar). */
  title: string;
  /** Backend system status (StatusResponse.system_status). */
  status?: string | null;
  /** Backend timestamp (StatusResponse.timestamp). */
  timestamp?: string | null;
  /** Data quality status (StatusResponse.intelligence.data_quality.status). */
  dataQuality?: string | null;
  /** Composition-layer extras (e.g. refresh control). */
  children?: React.ReactNode;
}

export function Header({ title, status, timestamp, dataQuality, children }: HeaderProps): JSX.Element {
  const color = status ? getStatusColor(status) : "#8A8A9A";
  const label = status ? getStatusLabel(status) : "Unknown";

  return (
    <div className="flex items-center justify-between gap-4 border-b border-border bg-surface px-6 py-4">
      <h1 className="text-lg font-semibold text-text-primary">{title}</h1>

      <div className="flex items-center gap-4">
        {dataQuality ? (
          <span aria-label={`Data quality ${dataQuality}`}>
            <span className="mr-1.5 text-xs text-text-secondary">Data:</span>
            <StatusDot status={dataQuality} />
          </span>
        ) : null}

        {timestamp ? (
          <span className="text-xs text-text-secondary">{formatDateTime(timestamp)}</span>
        ) : null}

        <span aria-label="System status" className="flex items-center gap-2">
          <span
            aria-hidden="true"
            className="inline-block h-2 w-2 rounded-full"
            style={{ backgroundColor: color }}
          />
          <span className="text-sm text-text-primary">{label}</span>
        </span>

        {children}
      </div>
    </div>
  );
}

/**
 * Status indicator for use as a colored dot.
 */
function StatusDot({ status }: { status: string }): JSX.Element {
  return (
    <span
      aria-hidden="true"
      className="inline-block h-2.5 w-2.5 rounded-full align-middle"
      style={{ backgroundColor: getStatusColor(status) }}
    />
  );
}