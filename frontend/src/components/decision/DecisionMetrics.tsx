/**
 * DecisionMetrics — Key quantitative decision metrics.
 *
 * ⚠️  Presentational ONLY. Does NOT compute any value.
 */
interface DecisionMetricsProps {
  edgeRatio: number;
  netReturn: number;         // in bps
  positionSize: number;      // in units
  expectedReturn: number;    // [0, 1] or raw
}

function formatPositionSize(size: number): string {
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 0,
  }).format(size);
}

export function DecisionMetrics({
  edgeRatio,
  netReturn,
  positionSize,
  expectedReturn,
}: DecisionMetricsProps): JSX.Element {
  const metrics = [
    { label: "Edge Ratio",       value: edgeRatio.toFixed(2),                  hint: "Risk-adjusted edge" },
    { label: "Net Return",       value: `${netReturn.toFixed(2)} bps`,         hint: "After costs" },
    { label: "Position Size",    value: formatPositionSize(positionSize),      hint: "Suggested exposure" },
    { label: "Expected Return",  value: `${(expectedReturn * 100).toFixed(2)}%`, hint: "Model estimate" },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {metrics.map((m) => (
        <div key={m.label} className="bg-panel rounded-lg border border-line p-4">
          <div className="text-xs uppercase tracking-wider text-muted">{m.label}</div>
          <div className="text-xl font-bold font-mono text-ink mt-1">{m.value}</div>
          <div className="text-xs text-muted mt-1">{m.hint}</div>
        </div>
      ))}
    </div>
  );
}
