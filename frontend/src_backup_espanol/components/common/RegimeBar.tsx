/**
 * Regime bar — presentational only.
 *
 * Receives the macro regime from DriversResponse.macro_regime (Layer 3) and
 * renders each axis verbatim. AUDIT: the "Market Regime" panel on the Global
 * Overview (mockup) has NO contract stream (G4) — compositions pass null and
 * render NotAvailable. VIX / risk-appetite values are NOT contractual and are
 * never derived here.
 */
import type { MacroRegime } from "../../types/contracts";
import { formatStatus } from "../../utils";
import { NotAvailable } from "./NotAvailable";

interface RegimeBarProps {
  /** Backend macro regime — null when unavailable. */
  macroRegime: MacroRegime | null;
  /** Dialog that tells the user why the regime is unavailable. */
  unavailableReason?: string;
}

export function RegimeBar({
  macroRegime,
  unavailableReason = "UNSUPPORTED_BY_CONTRACT: no RegimeResponse stream (G4).",
}: RegimeBarProps): JSX.Element {
  if (!macroRegime) return <NotAvailable feature="Market Regime" reason={unavailableReason} />;

  const axes: Array<{ key: string; label: string; value: string }> = [
    { key: "risk", label: "Risk", value: formatStatus(macroRegime.risk) },
    { key: "policy", label: "Policy", value: formatStatus(macroRegime.policy) },
    { key: "growth", label: "Growth", value: formatStatus(macroRegime.growth) },
    { key: "inflation", label: "Inflation", value: formatStatus(macroRegime.inflation) },
  ];

  return (
    <div className="flex flex-wrap items-center gap-3">
      {axes.map((axis) => (
        <div
          key={axis.key}
          className="flex items-center gap-2 rounded-lg border border-border bg-background px-3 py-1.5"
        >
          <span className="text-xs text-text-secondary">{axis.label}</span>
          <span className="text-sm font-semibold text-text-primary">{axis.value}</span>
        </div>
      ))}
    </div>
  );
}