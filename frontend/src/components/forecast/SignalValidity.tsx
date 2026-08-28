/**
 * Signal validity — presentational only.
 *
 * Mockup "⚠️ SIGNAL VALIDITY". Layer 1 exposes decision validity only through
 * StatusResponse.intelligence.decision_validity (and the decision rejection
 * reason through lineage). The mockup's condition lists ("remains valid while",
 * "invalidated if") are NOT contract fields → NotAvailable. NO_DERIVATION.
 */
import type { DecisionValidity } from "../../types/contracts";
import { getStatusColor, getStatusLabel } from "../../utils/status";
import { NotAvailable } from "../common/NotAvailable";

interface SignalValidityProps {
  /** Backend decision validity (StatusResponse.intelligence.decision_validity). */
  decisionValidity?: DecisionValidity | null;
}

export function SignalValidity({ decisionValidity }: SignalValidityProps): JSX.Element {
  if (!decisionValidity) {
    return (
      <NotAvailable
        feature="signal-validity"
        reason="UNSUPPORTED_BY_CONTRACT: invalidation conditions not in Layer 1 §7"
      />
    );
  }

  return (
    <div className="flex flex-col gap-3 rounded-lg border border-border bg-surface p-6">
      <h2 className="text-sm font-semibold text-text-primary">Signal Validity</h2>
      <div className="flex items-center gap-2 text-sm">
        <span
          aria-hidden="true"
          className="inline-block h-2 w-2 rounded-full"
          style={{ backgroundColor: getStatusColor(decisionValidity) }}
        />
        <span className="font-medium text-text-primary">
          {getStatusLabel(decisionValidity)}
        </span>
      </div>
      <p className="text-xs text-text-secondary">
        Invalidation conditions are not exposed by the Layer 1 contract.
      </p>
    </div>
  );
}