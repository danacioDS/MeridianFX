/**
 * DecisionHero — Top-level decision presentation.
 *
 * ⚠️  Presentational ONLY. Does NOT compute direction, confidence,
 *     actionability, or validity. All values come from the backend.
 */
interface DecisionHeroProps {
  direction: string;         // LONG | SHORT | NEUTRAL
  confidence: number;        // [0, 1]
  actionable: boolean;
  signalValidity: string;    // VALID | DEGRADED | UNAVAILABLE
}

const DIRECTION_STYLES: Record<string, { color: string; bg: string; border: string; icon: string }> = {
  LONG:    { color: "text-bull",   bg: "bg-bull/10",   border: "border-bull/40",   icon: "▲" },
  SHORT:   { color: "text-bear",   bg: "bg-bear/10",   border: "border-bear/40",   icon: "▼" },
  NEUTRAL: { color: "text-muted",  bg: "bg-panel-2",   border: "border-line",      icon: "—" },
};

const VALIDITY_STYLES: Record<string, { color: string; bg: string; border: string; icon: string }> = {
  VALID:       { color: "text-bull",   bg: "bg-bull/10",   border: "border-bull/40",   icon: "✓" },
  DEGRADED:    { color: "text-amber",  bg: "bg-amber/10",  border: "border-amber/40",  icon: "⚠" },
  UNAVAILABLE: { color: "text-muted",  bg: "bg-panel-2",   border: "border-line",      icon: "✗" },
};

export function DecisionHero({
  direction,
  confidence,
  actionable,
  signalValidity,
}: DecisionHeroProps): JSX.Element {
  const dirStyle = DIRECTION_STYLES[direction] ?? DIRECTION_STYLES.NEUTRAL;
  const valStyle = VALIDITY_STYLES[signalValidity] ?? VALIDITY_STYLES.UNAVAILABLE;

  return (
    <div className={`rounded-lg border ${dirStyle.border} ${dirStyle.bg} p-6`}>
      <div className="flex flex-wrap items-center justify-between gap-6">
        {/* Direction + Confidence */}
        <div className="flex items-center gap-6">
          <div className={`text-5xl font-bold ${dirStyle.color}`}>
            {dirStyle.icon}
          </div>
          <div>
            <div className={`text-3xl font-bold ${dirStyle.color}`}>
              {direction}
            </div>
            <div className="text-sm text-muted mt-1">
              Confidence {(confidence * 100).toFixed(1)}%
            </div>
          </div>
        </div>

        {/* Actionable + Validity */}
        <div className="flex flex-col gap-2 items-end">
          <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-semibold ${
            actionable
              ? "text-bull bg-bull/10 border border-bull/40"
              : "text-muted bg-panel-2 border border-line"
          }`}>
            {actionable ? "✅ ACTIONABLE" : "⏸ NOT ACTIONABLE"}
          </div>
          <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium ${valStyle.color} ${valStyle.bg} border ${valStyle.border}`}>
            {valStyle.icon} {signalValidity}
          </div>
        </div>
      </div>
    </div>
  );
}
