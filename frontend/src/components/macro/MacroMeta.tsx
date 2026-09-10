/**
 * MacroMeta — Data availability and metadata.
 *
 * ⚠️  Presentational ONLY.
 */
interface MacroMetaProps {
  base: string;
  quote: string;
  baseAvailable: boolean;
  quoteAvailable: boolean;
  reason: string | null;
}

export function MacroMeta({
  base,
  quote,
  baseAvailable,
  quoteAvailable,
  reason,
}: MacroMetaProps): JSX.Element {
  return (
    <div className="space-y-3 text-sm">
      <div className="flex justify-between border-b border-line pb-2">
        <span className="text-muted">Base</span>
        <span className="font-semibold text-ink">
          {base || "—"} · {baseAvailable ? "AVAILABLE" : "UNAVAILABLE"}
        </span>
      </div>

      <div className="flex justify-between border-b border-line pb-2">
        <span className="text-muted">Quote</span>
        <span className="font-semibold text-ink">
          {quote || "—"} · {quoteAvailable ? "AVAILABLE" : "UNAVAILABLE"}
        </span>
      </div>

      {reason && (
        <div className="mt-3 text-xs text-amber">
          {reason}
        </div>
      )}
    </div>
  );
}
