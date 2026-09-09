/**
 * Economic filter — presentational only.
 *
 * Mockup "💰 ECONOMIC FILTER". Contract fields map as follows:
 *   - Net Return            → decision.net_return
 *   - Edge Ratio            → decision.edge_ratio
 *   - ACTIONABLE            → decision.actionable
 *   - Gross Return          → decision.net_return (mockup shows gross, contract
 *                             exposes only net) → shown as Net Return only.
 *   - Total Costs / Spread / Slippage / Fees / Minimum Edge → NOT contractual
 *                             (no cost-breakdown fields in Layer 1 §7) →
 *                             NotAvailable. NO_FALLBACK_ALLOWED.
 */
import type { Decision } from "../../types/contracts";
import { formatEdgeRatio, formatNumber, formatPercent } from "../../utils";
import { getSignalStrengthLabel } from "../../utils/status";
import { NotAvailable } from "../common/NotAvailable";

interface EconomicFilterProps {
  /** Decision payload — present only when delivery_state is ELIGIBLE. */
  decision: Decision | null;
}

export function EconomicFilter({ decision }: EconomicFilterProps): JSX.Element {
  if (!decision) {
    return (
      <NotAvailable
        feature="economic-filter"
        reason="UNSUPPORTED_BY_CONTRACT: decision payload absent (delivery_state not ELIGIBLE)"
      />
    );
  }

  return (
    <div className="flex flex-col gap-4 rounded-lg border border-border bg-surface p-6">
      <h2 className="text-sm font-semibold text-text-primary">Economic Filter</h2>

      <dl className="grid grid-cols-2 gap-x-6 gap-y-3 text-sm">
        <div className="flex items-baseline justify-between gap-2">
          <dt className="text-xs text-text-secondary">Net Return</dt>
          <dd className="font-medium text-text-primary">{formatPercent(decision.net_return)}</dd>
        </div>
        <div className="flex items-baseline justify-between gap-2">
          <dt className="text-xs text-text-secondary">Edge Ratio</dt>
          <dd className="font-medium text-text-primary">{formatEdgeRatio(decision.edge_ratio)}</dd>
        </div>
        <div className="flex items-baseline justify-between gap-2">
          <dt className="text-xs text-text-secondary">Signal Strength</dt>
          <dd className="font-medium text-text-primary">
            {getSignalStrengthLabel(decision.signal_strength)}
          </dd>
        </div>
        <div className="flex items-baseline justify-between gap-2">
          <dt className="text-xs text-text-secondary">Confidence</dt>
          <dd className="font-medium text-text-primary">
            {formatNumber(decision.confidence, 2)}
          </dd>
        </div>
      </dl>

      <div className="rounded-lg border border-border bg-background p-3 text-xs text-text-secondary">
        <p className="font-medium text-text-primary">Cost breakdown</p>
        <p className="mt-1">
          Total costs / spread / slippage / fees / minimum edge are not exposed by the Layer 1
          contract.
        </p>
      </div>

      <StatusPill actionable={decision.actionable} />
    </div>
  );
}

function StatusPill({ actionable }: { actionable: boolean }): JSX.Element {
  return (
    <span
      className={`inline-flex w-fit items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold ${
        actionable ? "bg-primary/15 text-primary" : "border border-border text-text-secondary"
      }`}
      aria-label={actionable ? "Actionable" : "Not actionable"}
    >
      <span
        aria-hidden="true"
        className="inline-block h-1.5 w-1.5 rounded-full"
        style={{ backgroundColor: actionable ? "#00D4AA" : "#8A8A9A" }}
      />
      {actionable ? "Actionable" : "No edge"}
    </span>
  );
}