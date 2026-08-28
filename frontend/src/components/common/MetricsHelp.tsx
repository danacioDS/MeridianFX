/**
 * Metrics Help — presentational only.
 * 
 * Explica qué significa cada métrica en el ranking
 */
interface MetricHelpProps {
  pair?: string;
}

export function MetricsHelp({ pair = "GBP/USD" }: MetricHelpProps): JSX.Element {
  return (
    <div className="border border-border rounded-lg bg-surface p-4 space-y-3">
      <div className="flex items-center gap-2 text-sm font-semibold text-text-primary">
        <span>📖</span> Understanding the Metrics
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
        {/* Bearish */}
        <div className="bg-surface-2 rounded-lg p-3 space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-[#C4453A] font-bold">▼ Bearish</span>
            <span className="text-xs text-text-secondary">Signal Direction</span>
          </div>
          <p className="text-text-secondary text-xs leading-relaxed">
            The model predicts <strong className="text-text-primary">{pair}</strong> will <strong className="text-[#C4453A]">decrease</strong> in value.
            <br />
            <span className="text-text-secondary/70">↓ Bearish = USD strengthens against {pair.replace('USD/', '')}</span>
          </p>
        </div>

        {/* Probability */}
        <div className="bg-surface-2 rounded-lg p-3 space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-[#0E7C86] font-mono font-bold">70%</span>
            <span className="text-xs text-text-secondary">Probability</span>
          </div>
          <p className="text-text-secondary text-xs leading-relaxed">
            <strong className="text-text-primary">70% confidence</strong> that the predicted direction will occur.
            <br />
            <span className="text-text-secondary/70">↑ Higher probability = stronger conviction</span>
          </p>
        </div>

        {/* Edge Ratio */}
        <div className="bg-surface-2 rounded-lg p-3 space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-text-primary font-mono font-bold">0.92x</span>
            <span className="text-xs text-text-secondary">Edge Ratio</span>
          </div>
          <p className="text-text-secondary text-xs leading-relaxed">
            <strong className="text-text-primary">Expected return ÷ Risk</strong> after costs.
            <br />
            <span className="text-text-secondary/70">↑ Higher edge = better risk-reward tradeoff</span>
          </p>
        </div>

        {/* No Edge */}
        <div className="bg-surface-2 rounded-lg p-3 space-y-1 border-l-2 border-[#C4453A]/30">
          <div className="flex items-center gap-2">
            <span className="text-text-secondary font-semibold">❌ No Edge</span>
            <span className="text-xs text-text-secondary">Actionability Status</span>
          </div>
          <p className="text-text-secondary text-xs leading-relaxed">
            <strong className="text-text-primary">0.92x &lt; Minimum Threshold</strong>
            <br />
            <span className="text-text-secondary/70">Edge ratio is too low to justify trading costs, slippage, and fees.</span>
          </p>
        </div>
      </div>

      {/* Additional explanation */}
      <div className="border-t border-border pt-3 mt-1">
        <div className="text-xs text-text-secondary leading-relaxed">
          <strong className="text-text-primary">Actionability Formula:</strong>
          <br />
          <span className="font-mono text-[11px]">
            Actionable = (Net Return &gt; Minimum Edge) AND (Probability &gt; Threshold) AND (Regime = Favorable)
          </span>
          <br />
          <span className="text-text-secondary/70">
            • <strong>Net Return</strong> = Gross Return − Spread − Slippage − Fees
          </span>
          <br />
          <span className="text-text-secondary/70">
            • <strong>Minimum Edge</strong> varies by pair (liquidity, transaction costs, volatility)
          </span>
        </div>
      </div>
    </div>
  );
}
