/**
 * Probability chart — presentational only.
 *
 * Mockup forecast probability visualization. History series are NOT exposed by
 * Layer 1 (gap G-01 getForecastHistory). This component accepts an optional
 * series via props and renders the availability state when no series exists —
 * it never synthesizes one.
 */
import { NotAvailable } from "../common/NotAvailable";

/** A single probability point (future stream; currently unavailable). */
export interface ProbabilityPoint {
  timestamp: string;
  probability: number;
}

interface ProbabilityChartProps {
  /** Probability history series (gap G-01 — currently always null). */
  data?: ProbabilityPoint[] | null;
}

export function ProbabilityChart({ data }: ProbabilityChartProps): JSX.Element {
  if (!data || data.length === 0) {
    return (
      <NotAvailable
        feature="forecast-probability-history"
        reason="UNSUPPORTED_BY_CONTRACT: no probability history stream (G-01 getForecastHistory)"
      />
    );
  }

  return (
    <div className="rounded-lg border border-border bg-surface p-5">
      <h3 className="mb-3 text-sm font-semibold text-text-primary">Forecast Probability</h3>
      <ol className="flex items-end gap-1">
        {data.map((point) => (
          <li
            key={point.timestamp}
            className="flex-1 rounded-t bg-primary/40"
            style={{ height: `${Math.round(Math.max(0, Math.min(1, point.probability)) * 96)}px` }}
            aria-label={`${point.timestamp}: ${point.probability}`}
          />
        ))}
      </ol>
    </div>
  );
}