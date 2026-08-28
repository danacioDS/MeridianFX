/**
 * Metrics Help — presentational only.
 * Explica qué significa cada métrica en el ranking
 * Versión con fuente más grande
 */
interface MetricHelpProps {
  pair?: string;
}

export function MetricsHelp({ pair = "GBP/USD" }: MetricHelpProps): JSX.Element {
  return (
    <div className="border border-line rounded-xl bg-panel p-5 space-y-4">
      <div className="flex items-center gap-2 text-base font-semibold text-ink">
        <span>📖</span> Understanding the Metrics
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-base">
        {/* Bearish */}
        <div className="bg-paper rounded-xl p-4 space-y-1.5 border border-line">
          <div className="flex items-center gap-2">
            <span className="text-[#C4453A] font-bold text-lg">▼ Bearish</span>
            <span className="text-sm text-muted">Signal Direction</span>
          </div>
          <p className="text-ink-soft text-base leading-relaxed">
            The model predicts <strong className="text-ink">{pair}</strong> will <strong className="text-[#C4453A]">decrease</strong> in value.
            <br />
            <span className="text-muted text-sm">↓ Bearish = USD strengthens against {pair.replace('USD/', '')}</span>
          </p>
        </div>

        {/* Probability */}
        <div className="bg-paper rounded-xl p-4 space-y-1.5 border border-line">
          <div className="flex items-center gap-2">
            <span className="text-[#0E7C86] font-mono font-bold text-lg">70%</span>
            <span className="text-sm text-muted">Probability</span>
          </div>
          <p className="text-ink-soft text-base leading-relaxed">
            <strong className="text-ink">70% confidence</strong> that the predicted direction will occur.
            <br />
            <span className="text-muted text-sm">↑ Higher probability = stronger conviction</span>
          </p>
        </div>

        {/* Edge Ratio */}
        <div className="bg-paper rounded-xl p-4 space-y-1.5 border border-line">
          <div className="flex items-center gap-2">
            <span className="text-ink font-mono font-bold text-lg">0.92x</span>
            <span className="text-sm text-muted">Edge Ratio</span>
          </div>
          <p className="text-ink-soft text-base leading-relaxed">
            <strong className="text-ink">Expected return ÷ Risk</strong> after costs.
            <br />
            <span className="text-muted text-sm">↑ Higher edge = better risk-reward tradeoff</span>
          </p>
        </div>

        {/* No Edge */}
        <div className="bg-paper rounded-xl p-4 space-y-1.5 border border-line border-l-4 border-l-[#C4453A]">
          <div className="flex items-center gap-2">
            <span className="text-muted font-semibold text-lg">❌ No Edge</span>
            <span className="text-sm text-muted">Actionability Status</span>
          </div>
          <p className="text-ink-soft text-base leading-relaxed">
            <strong className="text-ink">0.92x &lt; Minimum Threshold</strong>
            <br />
            <span className="text-muted text-sm">Edge ratio is too low to justify trading costs, slippage, and fees.</span>
          </p>
        </div>
      </div>

      {/* Additional explanation - más grande */}
      <div className="border-t border-line pt-4 mt-2">
        <div className="text-base text-ink-soft leading-relaxed">
          <strong className="text-ink">Actionability Formula:</strong>
          <br />
          <span className="font-mono text-sm">
            Actionable = (Net Return &gt; Minimum Edge) AND (Probability &gt; Threshold) AND (Regime = Favorable)
          </span>
          <br />
          <span className="text-muted text-sm">
            • <strong>Net Return</strong> = Gross Return − Spread − Slippage − Fees
          </span>
          <br />
          <span className="text-muted text-sm">
            • <strong>Minimum Edge</strong> varies by pair (liquidity, transaction costs, volatility)
          </span>
        </div>
      </div>
    </div>
  );
}
