/**
 * LeadingSignals — Top market signals from /v1/market-intelligence.
 *
 * ⚠️  Presentational ONLY. Direction ("bullish"/"bearish"), confidence,
 *     edge_ratio, and opportunity_score all come from the backend.
 *     No transformation of economic semantics is performed here.
 */
interface LeadingSignal {
  pair: string;
  direction: string;         // "bullish" | "bearish"
  confidence: number;        // [0, 1]
  edge_ratio: number;
  opportunity_score: number;
  actionable: boolean;
}

interface LeadingSignalsProps {
  signals: LeadingSignal[];
}

export function LeadingSignals({ signals }: LeadingSignalsProps): JSX.Element {
  if (!signals || signals.length === 0) {
    return (
      <div className="text-sm text-muted py-4 text-center">
        No leading signals available
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {signals.map((signal, idx) => {
        const isBullish = signal.direction.toLowerCase() === "bullish";
        const confidencePercent = (signal.confidence * 100).toFixed(1);
        const edge = signal.edge_ratio.toFixed(2);

        return (
          <div
            key={signal.pair}
            className="flex items-center gap-4 py-2.5 px-3 rounded-lg hover:bg-panel-2 transition-colors text-sm"
          >
            <span className="font-mono text-muted text-xs w-6">
              #{idx + 1}
            </span>
            <span className="font-semibold text-ink w-24">
              {signal.pair}
            </span>
            <span
              className={`flex items-center gap-1.5 font-semibold w-28 ${
                isBullish ? "text-bull" : "text-bear"
              }`}
            >
              {isBullish ? "▲" : "▼"} {signal.direction}
            </span>
            <span className="font-mono text-ink-soft w-20">
              {confidencePercent}%
            </span>
            <span className="font-mono text-muted text-xs">
              edge {edge}x
            </span>
            {signal.actionable && (
              <span className="ml-auto text-xs px-2 py-0.5 rounded-full bg-bull-soft text-bull font-semibold">
                ACTIONABLE
              </span>
            )}
          </div>
        );
      })}
    </div>
  );
}
