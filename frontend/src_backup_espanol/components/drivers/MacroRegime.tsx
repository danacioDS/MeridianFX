/**
 * Macro regime — presentational only.
 *
 * Delegates to the shared common/RegimeBar (regime axes rendered verbatim).
 */
import type { MacroRegime as MacroRegimeT } from "../../types/contracts";
import { NotAvailable, RegimeBar } from "../common";

interface MacroRegimeProps {
  /** Backend macro regime. */
  macroRegime: MacroRegimeT | null;
}

export function MacroRegime({ macroRegime }: MacroRegimeProps): JSX.Element {
  if (!macroRegime) {
    return (
      <NotAvailable
        feature="Macro Regime"
        reason="UNSUPPORTED_BY_CONTRACT: no macro regime data available"
      />
    );
  }

  return <RegimeBar macroRegime={macroRegime} />;
}
