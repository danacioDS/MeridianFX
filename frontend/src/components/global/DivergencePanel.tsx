/**
 * DivergencePanel — Z-score and interpretation for regime divergence.
 *
 * Displays the current divergence z-score between the observed price
 * and the clean-float ARIMA(1,0,1) projection. Narrative generation
 * (LLM) is not yet wired; this component only surfaces the statistic
 * and a short static explanation.
 */
interface DivergencePanelProps {
  pair: string;
  windowDays: number;
  currentZscore: number | null;
  interpretation: string;
  regime: string;
}

const INTERPRETATION_LABEL: Record<string, string> = {
  normal: "Within expected range",
  notable: "Notable divergence",
  extreme: "Extreme divergence",
  persistent: "Persistent divergence",
  unavailable: "Insufficient data",
};

const INTERPRETATION_COLOR: Record<string, string> = {
  normal: "text-bull",
  notable: "text-amber",
  extreme: "text-bear",
  persistent: "text-bear font-bold",
  unavailable: "text-muted",
};

export function DivergencePanel({
  pair,
  windowDays,
  currentZscore,
  interpretation,
  regime,
}: DivergencePanelProps): JSX.Element {
  const label = INTERPRETATION_LABEL[interpretation] ?? interpretation;
  const colorClass =
    INTERPRETATION_COLOR[interpretation] ?? "text-muted";

  return (
    <div className="rounded-xl border border-line bg-panel-2 p-5">
      <div className="text-xs uppercase tracking-wider text-muted mb-3">
        📉 Divergence vs clean-float baseline
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <div className="text-xs text-muted">Current z-score</div>
          <div className={`text-2xl font-mono font-bold ${colorClass}`}>
            {currentZscore !== null ? currentZscore.toFixed(2) : "—"}
          </div>
          <div className={`text-xs ${colorClass}`}>{label}</div>
        </div>

        <div>
          <div className="text-xs text-muted">Window</div>
          <div className="text-2xl font-mono font-bold text-ink">
            {windowDays}d
          </div>
          <div className="text-xs text-muted">rolling</div>
        </div>

        <div>
          <div className="text-xs text-muted">Regime</div>
          <div className="text-2xl font-mono font-bold text-ink">
            {regime}
          </div>
          <div className="text-xs text-muted">{pair}</div>
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-line text-xs text-muted leading-relaxed space-y-3">
        <p>
          The z-score measures how many standard deviations the observed
          price is from the projection of a rolling ARIMA(1,0,1) model
          under a clean-float assumption.
        </p>

        <div>
          <div className="text-muted mb-1.5">Interpretation thresholds:</div>
          <table className="w-full text-xs">
            <tbody>
              <tr>
                <td className="py-0.5 pr-4 font-mono">|z| &lt; 1.0</td>
                <td className="py-0.5 text-bull">Within expected range</td>
                <td className="py-0.5 pl-4 text-muted/70">
                  ≈ 68% of a normal distribution
                </td>
              </tr>
              <tr>
                <td className="py-0.5 pr-4 font-mono">1.0 – 2.0</td>
                <td className="py-0.5 text-amber">Notable divergence</td>
                <td className="py-0.5 pl-4 text-muted/70">
                  outside ±1σ
                </td>
              </tr>
              <tr>
                <td className="py-0.5 pr-4 font-mono">2.0 – 3.0</td>
                <td className="py-0.5 text-bear">Extreme divergence</td>
                <td className="py-0.5 pl-4 text-muted/70">
                  outside ±2σ (≈ 5% chance)
                </td>
              </tr>
              <tr>
                <td className="py-0.5 pr-4 font-mono">|z| ≥ 3.0</td>
                <td className="py-0.5 text-bear font-bold">
                  Persistent divergence
                </td>
                <td className="py-0.5 pl-4 text-muted/70">
                  outside ±3σ (≈ 0.3% chance)
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <p className="italic">
          A high divergence is consistent with intervention but does not
          prove it causally. Other explanations (structural break,
          liquidity event, data error) are possible. See{" "}
          <span className="font-mono">docs/divergence/README.md</span>.
        </p>
      </div>
    </div>
  );
}
