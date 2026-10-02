/**
 * LayerColumn — one of the four columns of the Architecture Control Center.
 *
 * Renders the checks of a single layer with explicit status markers.
 * No analytical logic: it only maps status → color and icon.
 */
import type { CheckStatus, LayerEnvelope, LayerStatus } from "../../types/system";

const CHECK_ICON: Record<CheckStatus, string> = {
  OK: "✓",
  WARN: "⚠",
  FAIL: "✗",
};

const CHECK_COLOR: Record<CheckStatus, string> = {
  OK: "text-green-600",
  WARN: "text-amber-600",
  FAIL: "text-red-600",
};

const LAYER_BORDER: Record<LayerStatus, string> = {
  HEALTHY: "border-green-500",
  WARNING: "border-amber-500",
  DEGRADED: "border-red-500",
  UNKNOWN: "border-gray-400",
};

const LAYER_BADGE: Record<LayerStatus, string> = {
  HEALTHY: "bg-green-100 text-green-800",
  WARNING: "bg-amber-100 text-amber-800",
  DEGRADED: "bg-red-100 text-red-800",
  UNKNOWN: "bg-gray-100 text-gray-700",
};

interface Props {
  layer: LayerEnvelope;
}

export function LayerColumn({ layer }: Props): JSX.Element {
  return (
    <div className={`border-l-4 ${LAYER_BORDER[layer.status]} pl-4 flex flex-col gap-3`}>
      <div className="flex items-center justify-between">
        <h3 className="font-serif text-lg uppercase tracking-wide">
          {layer.layer}
        </h3>
        <span className={`text-xs font-mono font-semibold px-2 py-1 rounded ${LAYER_BADGE[layer.status]}`}>
          {layer.status}
        </span>
      </div>

      <ul className="space-y-2 text-sm font-mono">
        {layer.checks.map((c) => (
          <li key={c.id} className="flex gap-2 items-start">
            <span className={`${CHECK_COLOR[c.status]} shrink-0`}>{CHECK_ICON[c.status]}</span>
            <div className="flex-1">
              <div className="text-ink">{c.id}</div>
              <div className="text-xs text-ink-soft mt-0.5">{c.detail}</div>
              {c.finding && (
                <span className="inline-block mt-1 text-xs bg-meridian-soft text-meridian px-2 py-0.5 rounded">
                  {c.finding}
                </span>
              )}
            </div>
          </li>
        ))}
      </ul>

      {layer.findings.length > 0 && (
        <p className="text-xs text-ink-soft border-t border-line pt-2 mt-auto">
          Findings: <span className="font-mono">{layer.findings.join(", ")}</span>
        </p>
      )}
    </div>
  );
}
