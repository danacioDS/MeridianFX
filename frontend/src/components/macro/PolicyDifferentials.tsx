/**
 * PolicyDifferentials — Macro differentials and policy rates.
 *
 * ⚠️  Presentational ONLY. All values come from the backend.
 */
interface PolicyDifferentialsProps {
  base: string;
  quote: string;
  policyDifferential: number | null;
  growthDifferential: number | null;
  inflationDifferential: number | null;
  baseRate: number | null;
  quoteRate: number | null;
}

function formatDifferential(value: number | null): string {
  if (value == null) return "—";
  const sign = value >= 0 ? "+" : "";
  return `${sign}${value.toFixed(4)}`;
}

function formatRate(value: number | null): string {
  if (value == null) return "—";
  return `${value.toFixed(3)}%`;
}

export function PolicyDifferentials({
  base,
  quote,
  policyDifferential,
  growthDifferential,
  inflationDifferential,
  baseRate,
  quoteRate,
}: PolicyDifferentialsProps): JSX.Element {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-y-3 gap-x-6 text-sm">
      <div className="flex justify-between border-b border-line pb-2">
        <span className="text-muted">Policy differential</span>
        <span className="font-mono font-semibold text-ink">
          {formatDifferential(policyDifferential)}
        </span>
      </div>
      <div className="flex justify-between border-b border-line pb-2">
        <span className="text-muted">Growth differential</span>
        <span className="font-mono font-semibold text-ink">
          {formatDifferential(growthDifferential)}
        </span>
      </div>
      <div className="flex justify-between border-b border-line pb-2">
        <span className="text-muted">Inflation differential</span>
        <span className="font-mono font-semibold text-ink">
          {formatDifferential(inflationDifferential)}
        </span>
      </div>
      <div className="flex justify-between border-b border-line pb-2">
        <span className="text-muted">{base} rate</span>
        <span className="font-mono font-semibold text-ink">
          {formatRate(baseRate)}
        </span>
      </div>
      <div className="flex justify-between border-b border-line pb-2">
        <span className="text-muted">{quote} rate</span>
        <span className="font-mono font-semibold text-ink">
          {formatRate(quoteRate)}
        </span>
      </div>
    </div>
  );
}
