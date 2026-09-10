/**
 * DecisionShapPanel — Top SHAP drivers for the decision.
 *
 * ⚠️  Presentational ONLY. Orders by |value| (presentation choice).
 *     All SHAP values come from backend artifact.shap_values.
 */
import type { ShapValue } from "../../hooks/useCanonicalDecision";

interface DecisionShapPanelProps {
  shapValues: ShapValue[];
  maxItems?: number;
}

export function DecisionShapPanel({
  shapValues,
  maxItems = 10,
}: DecisionShapPanelProps): JSX.Element {
  if (!shapValues || shapValues.length === 0) {
    return (
      <div className="text-sm text-muted">
        No SHAP values available for this model.
      </div>
    );
  }

  const sorted = [...shapValues]
    .sort((a, b) => Math.abs(b.value) - Math.abs(a.value))
    .slice(0, maxItems);

  const maxAbs = Math.max(...sorted.map((s) => Math.abs(s.value)), 0.0000001);

  return (
    <div className="space-y-3">
      {sorted.map((s, idx) => {
        const isPositive = s.value >= 0;
        const width = Math.round((Math.abs(s.value) / maxAbs) * 100);

        return (
          <div key={`${s.feature}-${idx}`} className="space-y-1">
            <div className="flex justify-between items-baseline text-sm">
              <span className="font-medium text-ink">
                #{idx + 1} {s.feature}
              </span>
              <span className={`font-mono ${isPositive ? "text-bull" : "text-bear"}`}>
                {isPositive ? "▲" : "▼"} {s.value.toFixed(4)}
              </span>
            </div>

            <div className="w-full h-2 bg-panel-2 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full ${isPositive ? "bg-bull" : "bg-bear"}`}
                style={{ width: `${width}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
