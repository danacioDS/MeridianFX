/**
 * MarketIntelligenceHero — System-wide market intelligence summary.
 *
 * ⚠️  Presentational ONLY. All values come from /v1/market-intelligence.
 *     No scores, directions, or statuses are computed here.
 */
interface MarketIntelligenceHeroProps {
  status: string;              // "SELECTIVE" | ...
  marketCoverage: number;
  actionableCount: number;
  totalPairs: number;
  summary: string;
}

const STATUS_STYLES: Record<string, { color: string; bg: string; border: string; icon: string }> = {
  SELECTIVE:  { color: "text-amber",  bg: "bg-amber/10",  border: "border-amber/40",  icon: "🎯" },
  AGGRESSIVE: { color: "text-bull",   bg: "bg-bull/10",   border: "border-bull/40",   icon: "🟢" },
  DEFENSIVE:  { color: "text-bear",   bg: "bg-bear/10",   border: "border-bear/40",   icon: "🔴" },
};

export function MarketIntelligenceHero({
  status,
  marketCoverage,
  actionableCount,
  totalPairs,
  summary,
}: MarketIntelligenceHeroProps): JSX.Element {
  const styles = STATUS_STYLES[status] ?? STATUS_STYLES.SELECTIVE;

  return (
    <div className={`rounded-xl border ${styles.border} ${styles.bg} p-6`}>
      <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{styles.icon}</span>
          <div>
            <div className="text-xs uppercase tracking-wider text-muted">
              Decision Layer
            </div>
            <div className={`text-2xl font-bold ${styles.color}`}>
              {status}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-6 text-sm">
          <div className="text-center">
            <div className="text-xs text-muted">Coverage</div>
            <div className="text-xl font-bold font-mono text-ink">
              {marketCoverage}
            </div>
          </div>
          <div className="text-center">
            <div className="text-xs text-muted">Actionable</div>
            <div className={`text-xl font-bold font-mono ${
              actionableCount > 0 ? "text-bull" : "text-muted"
            }`}>
              {actionableCount}
            </div>
          </div>
          <div className="text-center">
            <div className="text-xs text-muted">Total Pairs</div>
            <div className="text-xl font-bold font-mono text-ink">
              {totalPairs}
            </div>
          </div>
        </div>
      </div>

      <p className="text-sm text-ink-soft leading-relaxed border-t border-line pt-4">
        {summary}
      </p>
    </div>
  );
}
