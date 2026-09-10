/**
 * MacroHero — Top-level macro summary.
 *
 * ⚠️  Presentational ONLY. All values come from the backend.
 */
interface MacroRegime {
  risk: string;
  policy: string;
  growth: string;
  inflation: string;
}

interface MacroHeroProps {
  regime: string;
  macroRegime: MacroRegime | null;
  macroStatus: string;
  macroScore: number | null;
}

const STATUS_STYLES: Record<string, { color: string; bg: string; border: string }> = {
  FULL:        { color: "text-bull",   bg: "bg-bull/10",   border: "border-bull/40" },
  PARTIAL:     { color: "text-amber",  bg: "bg-amber/10",  border: "border-amber/40" },
  UNAVAILABLE: { color: "text-muted",  bg: "bg-panel-2",   border: "border-line" },
};

export function MacroHero({
  regime,
  macroRegime,
  macroStatus,
  macroScore,
}: MacroHeroProps): JSX.Element {
  const statusStyle = STATUS_STYLES[macroStatus] ?? STATUS_STYLES.UNAVAILABLE;

  return (
    <div className="rounded-lg border border-line bg-panel-2 p-6">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
        <div>
          <div className="text-xs uppercase tracking-wider text-muted">
            Current regime
          </div>
          <div className="text-2xl font-semibold text-ink mt-1">
            {regime || "UNKNOWN"}
          </div>
        </div>

        <span
          className={`inline-block px-3 py-1 rounded-full text-xs font-semibold border ${statusStyle.color} ${statusStyle.bg} ${statusStyle.border}`}
        >
          {macroStatus || "—"}
        </span>
      </div>

      {macroRegime ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div className="text-xs text-muted">Risk</div>
            <div className="font-semibold text-ink">{macroRegime.risk}</div>
          </div>
          <div>
            <div className="text-xs text-muted">Policy</div>
            <div className="font-semibold text-ink">{macroRegime.policy}</div>
          </div>
          <div>
            <div className="text-xs text-muted">Growth</div>
            <div className="font-semibold text-ink">{macroRegime.growth}</div>
          </div>
          <div>
            <div className="text-xs text-muted">Inflation</div>
            <div className="font-semibold text-ink">{macroRegime.inflation}</div>
          </div>
        </div>
      ) : (
        <div className="text-sm text-muted">No macro regime available.</div>
      )}

      <div className="mt-4 pt-4 border-t border-line">
        <div className="text-xs text-muted">Macro Score</div>
        <div className="text-xl font-bold font-mono text-ink">
          {macroScore != null ? macroScore.toFixed(4) : "—"}
        </div>
      </div>
    </div>
  );
}
