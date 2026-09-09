/**
 * Infrastructure status — presentational only.
 *
 * Renders StatusResponse.infrastructure blocks (api / database / pipeline /
 * cache) via the shared StatusBadge. No inference of component health.
 */
import type { InfrastructureStatus } from "../../types/contracts";
import { StatusBadge } from "../common/StatusBadge";

interface InfrastructureStatusProps {
  /** Infrastructure block. */
  infraStatus: InfrastructureStatus | null;
}

export function InfrastructureStatus({
  infraStatus,
}: InfrastructureStatusProps): JSX.Element {
  if (!infraStatus) {
    return (
      <div className="rounded-lg border border-border bg-surface p-4 text-xs text-text-secondary">
        Infrastructure status not provided.
      </div>
    );
  }

  const components: Array<[string, string]> = [
    ["API", infraStatus.api],
    ["Database", infraStatus.database],
    ["Pipeline", infraStatus.pipeline],
    ["Cache", infraStatus.cache],
  ];

  return (
    <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
      {components.map(([label, level]) => (
        <div
          key={label}
          className="flex flex-col items-start gap-1.5 rounded-lg border border-border bg-surface p-4"
        >
          <span className="text-xs text-text-secondary">{label}</span>
          <StatusBadge status={level} />
        </div>
      ))}
    </div>
  );
}