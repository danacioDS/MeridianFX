/**
 * Early warnings — UNSUPPORTED.
 *
 * Mockup "⚠️ EARLY WARNINGS". Layer 1 v5.1 defines no EarlyWarning response
 * structure, and no RankingResponse stream carries them (G-08). Per the
 * contract: render NotAvailable; never synthesize warnings from fields.
 */
import { NotAvailable } from "../common/NotAvailable";

export function EarlyWarnings(): JSX.Element {
  return (
    <NotAvailable
      feature="early-warnings"
      reason="UNSUPPORTED_BY_CONTRACT: no early-warning structure in Layer 1 v5.1 §7 (G-08)"
    />
  );
}