/**
 * EconomicBreakdown — Detailed economic filter breakdown.
 *
 * ⚠️  Presentational ONLY. All values in bps come from the backend.
 */
interface EconomicBreakdownProps {
  grossReturn: number;         // bps
  carryProxy: number;          // bps
  totalCost: number;           // bps
  netReturn: number;           // bps
  edgeRatio: number;
  requiredMinimumEdge: number;
  spread: number;              // bps
  slippage: number;            // bps
  commission: number;          // bps
}

export function EconomicBreakdown({
  grossReturn,
  carryProxy,
  totalCost,
  netReturn,
  edgeRatio,
  requiredMinimumEdge,
  spread,
  slippage,
  commission,
}: EconomicBreakdownProps): JSX.Element {
  const edgePasses = edgeRatio >= requiredMinimumEdge;

  return (
    <div className="space-y-4">
      <div className="bg-panel-2 rounded-lg p-4 border border-line space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-muted">Directional Gross Return</span>
          <span className="font-mono font-semibold text-ink">
            {grossReturn >= 0 ? "+" : ""}
            {grossReturn.toFixed(2)} bps
          </span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-muted">Carry Proxy</span>
          <span className="font-mono font-semibold text-ink">
            {carryProxy >= 0 ? "+" : ""}
            {carryProxy.toFixed(2)} bps
          </span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-muted">Total Cost</span>
          <span className="font-mono font-semibold text-bear">
            −{totalCost.toFixed(2)} bps
          </span>
        </div>
        <div className="border-t border-line pt-2 flex justify-between">
          <span className="text-sm font-semibold text-ink">Net Return</span>
          <span
            className={`font-mono font-bold ${
              netReturn >= 0 ? "text-bull" : "text-bear"
            }`}
          >
            {netReturn >= 0 ? "+" : ""}
            {netReturn.toFixed(2)} bps
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="bg-panel-2 rounded-lg p-3 border border-line">
          <div className="text-xs text-muted">Edge Ratio</div>
          <div
            className={`text-lg font-bold font-mono mt-1 ${
              edgePasses ? "text-bull" : "text-bear"
            }`}
          >
            {edgeRatio.toFixed(2)}
          </div>
        </div>
        <div className="bg-panel-2 rounded-lg p-3 border border-line">
          <div className="text-xs text-muted">Required Min Edge</div>
          <div className="text-lg font-bold font-mono text-ink mt-1">
            {requiredMinimumEdge.toFixed(2)}
          </div>
        </div>
      </div>

      <div>
        <div className="text-xs uppercase tracking-wider text-muted mb-2">
          Cost Breakdown
        </div>
        <div className="grid grid-cols-3 gap-2">
          <div className="text-center p-2 bg-panel-2 rounded border border-line">
            <div className="text-[10px] text-muted">Spread</div>
            <div className="text-sm font-mono font-semibold text-ink">
              {spread.toFixed(3)}
            </div>
          </div>
          <div className="text-center p-2 bg-panel-2 rounded border border-line">
            <div className="text-[10px] text-muted">Slippage</div>
            <div className="text-sm font-mono font-semibold text-ink">
              {slippage.toFixed(3)}
            </div>
          </div>
          <div className="text-center p-2 bg-panel-2 rounded border border-line">
            <div className="text-[10px] text-muted">Commission</div>
            <div className="text-sm font-mono font-semibold text-ink">
              {commission.toFixed(3)}
            </div>
          </div>
        </div>
        <div className="text-[10px] text-muted text-center mt-1">
          All values in bps
        </div>
      </div>
    </div>
  );
}
