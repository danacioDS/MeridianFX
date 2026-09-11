/**
 * HardGates — Status of the hard gates that filter decisions.
 *
 * ⚠️  Presentational ONLY. All values come from the backend.
 */
interface HardGatesProps {
  gateResults: Record<string, boolean>;
  allPassed: boolean;
  thresholdsUsed: Record<string, number>;
  firstFailingGate: string | null;
}

const GATE_LABELS: Record<string, string> = {
  unavailable: "Unavailable",
  invalid: "Invalid",
  concentration: "Concentration",
  data_quality: "Data Quality",
  economic_filter: "Economic Filter",
  correlation: "Correlation",
  regime_misalignment: "Regime Misalignment",
};

function formatThreshold(key: string, value: number): string {
  if (key === "concentration") {
    return new Intl.NumberFormat("en-US").format(value);
  }
  return value.toFixed(2);
}

export function HardGates({
  gateResults,
  allPassed,
  thresholdsUsed,
  firstFailingGate,
}: HardGatesProps): JSX.Element {
  const entries = Object.entries(gateResults);

  if (entries.length === 0) {
    return (
      <div className="text-sm text-muted text-center py-4">
        No gate results available
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div
        className={`flex items-center gap-2 text-sm font-semibold px-3 py-2 rounded-lg ${
          allPassed
            ? "bg-bull-soft text-bull"
            : "bg-bear-soft text-bear"
        }`}
      >
        <span>{allPassed ? "✅" : "❌"}</span>
        <span>
          {allPassed
            ? "All gates passed"
            : `Blocked by: ${firstFailingGate ?? "unknown"}`}
        </span>
      </div>

      <div className="space-y-1.5">
        {entries.map(([key, passed]) => {
          const label = GATE_LABELS[key] ?? key;
          const threshold = thresholdsUsed[key];

          return (
            <div
              key={key}
              className="flex items-center justify-between py-1.5 px-3 rounded-lg hover:bg-panel-2 transition-colors text-sm"
            >
              <div className="flex items-center gap-2">
                <span>{passed ? "✅" : "❌"}</span>
                <span className="font-medium text-ink">{label}</span>
              </div>
              {threshold !== undefined && (
                <span className="font-mono text-xs text-muted">
                  threshold: {formatThreshold(key, threshold)}
                </span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
