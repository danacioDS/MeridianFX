/**
 * RiskDriversPanel — Container for the 5 canonical risk drivers.
 *
 * ⚠️  Presentational ONLY. Orders by contribution (backend-provided values).
 */
import type { RiskDriver } from "../../hooks/useCanonicalRisk";
import { RiskDriverBar } from "./RiskDriverBar";

interface RiskDriversPanelProps {
  drivers: RiskDriver[];
}

import { EmptyState } from "../common";

export function RiskDriversPanel({ drivers }: RiskDriversPanelProps): JSX.Element {
  if (!drivers || drivers.length === 0) {
    return (
      <div className="text-sm text-muted">
        <EmptyState title="No risk drivers available" />
      </div>
    );
  }

  // Sort by contribution descending (presentation choice, not analytical)
  const sorted = [...drivers].sort((a, b) => b.contribution - a.contribution);
  const maxContribution = Math.max(...sorted.map((d) => d.contribution), 1);

  return (
    <div className="space-y-4">
      {sorted.map((driver) => (
        <RiskDriverBar
          key={driver.name}
          driver={driver}
          maxContribution={maxContribution}
        />
      ))}
    </div>
  );
}
