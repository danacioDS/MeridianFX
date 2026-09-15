/**
 * Actionable Info — Explains what "Actionable" means and the statistical
 * formula behind the decision. Presentational ONLY. No thresholds are
 * hardcoded. If the backend does not provide requiredMinimumEdge, the
 * component renders an "unavailable" state instead of inventing values.
 */

interface ActionableInfoProps {
  /** Required minimum edge in bps, from the backend. Null/undefined → unavailable. */
  requiredMinimumEdge?: number | null;
}

export function ActionableInfo({
  requiredMinimumEdge,
}: ActionableInfoProps): JSX.Element {
  const hasEvaluation = requiredMinimumEdge != null;

  return (
    <div className="rounded-lg border border-border bg-surface p-5 mt-4">
      <h4 className="text-sm font-semibold text-text-primary mb-3">
        📊 What does "Actionable" mean?
      </h4>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
        {/* Column 1: Definition */}
        <div className="bg-panel-2 rounded-lg p-4">
          <div className="text-xs text-muted uppercase tracking-wider mb-2">
            Definition
          </div>
          <p className="text-text-primary leading-relaxed">
            An opportunity is{" "}
            <span className="text-bull font-semibold">actionable</span> when
            the <strong>net edge</strong> (expected profit after costs)
            exceeds the minimum threshold defined by the system.
          </p>
          <p className="text-text-secondary text-xs mt-2">
            A probable direction is not enough; the opportunity must be{" "}
            <strong>economically attractive</strong> after accounting for
            transaction costs, slippage, and commissions.
          </p>
        </div>

        {/* Column 2: Formula */}
        <div className="bg-panel-2 rounded-lg p-4">
          <div className="text-xs text-muted uppercase tracking-wider mb-2">
            Statistical Formula
          </div>
          <div className="font-mono text-xs text-text-primary space-y-1">
            <div>
              <span className="text-muted">1. Gross Return =</span> Expected
              Return
            </div>
            <div>
              <span className="text-muted">2. Net Return =</span> Gross - Spread
              - Slippage - Fees
            </div>
            <div>
              <span className="text-muted">3. Edge Ratio =</span> Net Return /
              Required Minimum Edge
            </div>
            <div>
              <span className="text-muted">4. Actionable when:</span>{" "}
              Edge Ratio ≥ 1.0 <span className="text-muted">AND</span> all hard gates pass
            </div>
          </div>
          <div className="mt-2 text-xs text-muted border-t border-border pt-2">
            <span className="font-mono">Volatility</span> = Annualized standard
            deviation of returns
          </div>
        </div>

        {/* Column 3: Theory */}
        <div className="bg-panel-2 rounded-lg p-4">
          <div className="text-xs text-muted uppercase tracking-wider mb-2">
            Theoretical Basis
          </div>
          <p className="text-text-primary leading-relaxed">
            The concept of <strong>edge</strong> comes from decision theory
            under uncertainty. A signal with high probability (e.g. 70%) is{" "}
            <span className="text-bear font-semibold">not enough</span> if the
            expected profit does not compensate for risk and costs.
          </p>
          <p className="text-text-secondary text-xs mt-2">
            Reference:{" "}
            <span className="font-mono">
              Sharpe Ratio, Kelly Criterion, Transaction Cost Analysis
            </span>
          </p>
        </div>
      </div>

      {/* Thresholds or unavailable state */}
      <div className="mt-3 pt-3 border-t border-border text-xs text-muted flex flex-wrap gap-4">
        {hasEvaluation ? (
          <>
            <div>
              🔹 <span className="text-text-primary">Required Minimum Edge:</span>{" "}
              {requiredMinimumEdge.toFixed(2)} bps
            </div>
            <div>
              💡 <span className="text-text-primary">Interpretation:</span>{" "}
              Edge Ratio &lt; 1.0 means Net Return is below the required minimum.
            </div>
          </>
        ) : (
          <div className="w-full">
            <div>
              ℹ️{" "}
              <span className="text-text-primary">
                No economic evaluation is available for this pair.
              </span>
            </div>
            <div className="mt-1 text-[11px]">
              The backend did not provide the minimum required edge, so no
              default value is shown.
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
