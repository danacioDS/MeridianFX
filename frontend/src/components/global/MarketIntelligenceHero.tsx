/**
 * MarketIntelligenceHero — System-wide market intelligence summary.
 *
 * ⚠️  Presentational ONLY. All values come from /v1/market-intelligence.
 *     No scores, directions, or statuses are computed here.
 *
 * When a selectedPairView is provided (from ?pair=...), the hero focuses
 * on that pair while keeping the global coverage/actionable/total counts.
 */
import type { MISelectedPairView } from "../../hooks/useMarketIntelligence";

interface MarketIntelligenceHeroProps {
  status: string;              // "SELECTIVE" | ...
  marketCoverage: number;
  actionableCount: number;
  totalPairs: number;
  summary: string;
  selectedPairView?: MISelectedPairView;
}

const STATUS_STYLES: Record<string, { color: string; bg: string; border: string; icon: string }> = {
  SELECTIVE:  { color: "text-amber",  bg: "bg-amber/10",  border: "border-amber/40",  icon: "🎯" },
  AGGRESSIVE: { color: "text-bull",   bg: "bg-bull/10",   border: "border-bull/40",   icon: "🟢" },
  DEFENSIVE:  { color: "text-bear",   bg: "bg-bear/10",   border: "border-bear/40",   icon: "🔴" },
};

const PAIR_STATUS_STYLES: Record<string, { color: string; label: string }> = {
  ACTIONABLE:     { color: "text-bull",  label: "ACCIONABLE" },
  NOT_ACTIONABLE: { color: "text-muted", label: "NO ACCIONABLE" },
  UNAVAILABLE:    { color: "text-amber", label: "MODEL_UNAVAILABLE" },
};

export function MarketIntelligenceHero({
  status,
  marketCoverage,
  actionableCount,
  totalPairs,
  summary,
  selectedPairView,
}: MarketIntelligenceHeroProps): JSX.Element {
  const styles = STATUS_STYLES[status] ?? STATUS_STYLES.SELECTIVE;

  const hasPairFocus = !!selectedPairView;
  const pairStatus = selectedPairView?.status ?? "NOT_ACTIONABLE";
  const pairStyles = PAIR_STATUS_STYLES[pairStatus] ?? PAIR_STATUS_STYLES.NOT_ACTIONABLE;

  const confidencePct = selectedPairView?.confidence != null
    ? (selectedPairView.confidence * 100).toFixed(1) + "%"
    : "—";

  const edgeRatio = selectedPairView?.edge_ratio != null
    ? selectedPairView.edge_ratio.toFixed(2) + "x"
    : "—";

  return (
    <div className={`rounded-xl border ${styles.border} ${styles.bg} p-6`}>
      {/* Header: status + counters */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{styles.icon}</span>
          <div>
            <div className="text-xs uppercase tracking-wider text-muted">
              Decision Layer
              {hasPairFocus && (
                <span className="text-ink ml-2">· {selectedPairView!.pair}</span>
              )}
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

      {/* Selected pair focus */}
      {hasPairFocus && selectedPairView!.available && (
        <div className="border-t border-line pt-4 mb-4">
          <div className="flex flex-wrap items-center gap-6 text-sm">
            <div>
              <div className="text-xs text-muted">Estado del par</div>
              <div className={`text-lg font-bold ${pairStyles.color}`}>
                {pairStyles.label}
              </div>
            </div>
            <div>
              <div className="text-xs text-muted">Dirección</div>
              <div className="text-lg font-bold font-mono text-ink">
                {selectedPairView!.direction ?? "—"}
              </div>
            </div>
            <div>
              <div className="text-xs text-muted">Confianza</div>
              <div className="text-lg font-bold font-mono text-ink">
                {confidencePct}
              </div>
            </div>
            <div>
              <div className="text-xs text-muted">Edge</div>
              <div className="text-lg font-bold font-mono text-ink">
                {edgeRatio}
              </div>
            </div>
            <div>
              <div className="text-xs text-muted">Quality</div>
              <div className="text-lg font-bold font-mono text-ink">
                {selectedPairView!.quality ?? "—"}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Narrative (pair-focused if available, else global) */}
      <p className="text-sm text-ink-soft leading-relaxed border-t border-line pt-4">
        {hasPairFocus && selectedPairView!.narrative
          ? selectedPairView!.narrative
          : summary}
      </p>
    </div>
  );
}
