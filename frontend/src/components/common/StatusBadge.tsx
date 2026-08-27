/**
 * Status badge — presentational only.
 *
 * Maps an existing backend status string to a color/label (misnomers avoided:
 * no inference, no derivation). If no label is passed, the backend status is
 * title-cased for display.
 */
import { getStatusColor, getStatusLabel } from "../../utils/status";

interface StatusBadgeProps {
  /** Backend status string (e.g. "healthy", "ACTIVE", "warning"). */
  status: string;
  /** Optional explicit label. Defaults to getStatusLabel(status). */
  label?: string;
}

export function StatusBadge({ status, label }: StatusBadgeProps): JSX.Element {
  const color = getStatusColor(status);
  const text = label ?? getStatusLabel(status);
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full border border-border bg-background px-2.5 py-0.5 text-xs font-medium text-text-primary"
      aria-label={text}
    >
      <span aria-hidden="true" className="h-2 w-2 rounded-full" style={{ backgroundColor: color }} />
      {text}
    </span>
  );
}