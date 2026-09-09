/**
 * Drift indicator — presentational only.
 *
 * Mockup "⚠️ DRIFT DETECTION". Renders PerformanceResponse.degradation
 * (Layer 4 classification) verbatim: drift severity, detected flag, and the
 * current vs historical Sharpe values.
 */
import type { PerformanceDegradation, DriftSeverity } from "../../types/contracts";
import { formatSharpe } from "../../utils";
import { getStatusColor } from "../../utils/status";
import { NotAvailable } from "../common/NotAvailable";

interface DriftIndicatorProps {
  /** PerformanceResponse.degradation. */
  degradation: PerformanceDegradation | null;
}

export function DriftIndicator({ degradation }: DriftIndicatorProps): JSX.Element {
  if (!degradation) {
    return (
      <NotAvailable
        feature="drift-detection"
        reason="UNSUPPORTED_BY_CONTRACT: degradation block absent"
      />
    );
  }

  return (
    <div className="flex flex-col gap-3 rounded-lg border border-border bg-surface p-5">
      <div className="flex items-center gap-2">
        <span
          aria-hidden="true"
          className="inline-block h-2.5 w-2.5 rounded-full"
          style={{ backgroundColor: getStatusColor(degradation.drift_severity) }}
        />
        <span className="text-sm font-semibold text-text-primary">
          Drift {dropSeverity(degradation.drift_severity)} —{" "}
          {degradation.drift_detected ? "Detected" : "Not Detected"}
        </span>
      </div>
      <div className="flex items-baseline justify-between text-xs">
        <span className="text-text-secondary">Current period Sharpe</span>
        <span className="font-medium text-text-primary">
          {formatSharpe(degradation.current_sharpe)}
        </span>
      </div>
      <div className="flex items-baseline justify-between text-xs">
        <span className="text-text-secondary">Historical baseline Sharpe</span>
        <span className="font-medium text-text-primary">
          {formatSharpe(degradation.historical_sharpe)}
        </span>
      </div>
    </div>
  );
}

function dropSeverity(severity: DriftSeverity): string {
  switch (severity) {
    case "none":
      return "None";
    case "warning":
      return "Warning";
    case "critical":
      return "Critical";
    default:
      return String(severity);
  }
}