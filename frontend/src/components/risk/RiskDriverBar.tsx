/**
 * RiskDriverBar — Single risk driver presentation.
 *
 * ⚠️  Presentational ONLY. Contribution and weight come from backend.
 */
import type { RiskDriver } from "../../hooks/useCanonicalRisk";

interface RiskDriverBarProps {
  driver: RiskDriver;
  maxContribution: number; // for relative bar width
}

const DRIVER_LABELS: Record<string, string> = {
  volatility: "Volatility",
  macro:      "Macro",
  model:      "Model",
  regime:     "Regime",
  edge:       "Edge",
};

export function RiskDriverBar({ driver, maxContribution }: RiskDriverBarProps): JSX.Element {
  const label = DRIVER_LABELS[driver.name] ?? driver.name;
  const pct = maxContribution > 0
    ? Math.min((driver.contribution / maxContribution) * 100, 100)
    : 0;

  return (
    <div className="space-y-1">
      <div className="flex justify-between items-baseline text-sm">
        <span className="font-medium text-ink">{label}</span>
        <span className="font-mono text-ink">
          {driver.contribution.toFixed(2)}
        </span>
      </div>

      <div className="w-full h-2 bg-panel-2 rounded-full overflow-hidden">
        <div
          className="h-full bg-meridian rounded-full transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>

      <div className="flex justify-between text-xs text-muted">
        <span>weight {(driver.weight * 100).toFixed(0)}%</span>
        <span>{driver.explanation}</span>
      </div>
    </div>
  );
}
