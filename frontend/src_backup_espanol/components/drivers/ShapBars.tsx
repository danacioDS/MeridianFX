/**
 * SHAP bars — presentational only.
 *
 * Mockup "🔍 KEY DRIVERS". Renders DriversResponse.shap contributions in the
 * backend-provided order/rank. Bar lengths are a visual mapping of the
 * contribution magnitude (VISUAL_COMPONENT). The sign (±) is read directly
 * from the contribution field — never re-derived.
 */
import type { ShapContribution } from "../../types/contracts";
import { formatNumber } from "../../utils";
import { NotAvailable } from "../common/NotAvailable";

interface ShapBarsProps {
  /** SHAP contributions from DriversResponse.shap. */
  shap: ShapContribution[] | null;
}

export function ShapBars({ shap }: ShapBarsProps): JSX.Element {
  if (!shap || shap.length === 0) {
    return (
      <NotAvailable
        feature="key-drivers"
        reason="UNSUPPORTED_BY_CONTRACT: shap contributions not produced (drivers payload absent)"
      />
    );
  }

  const maxMagnitude = Math.max(...shap.map((c) => Math.abs(c.contribution)), 0.0000001);

  return (
    <div className="flex flex-col gap-3">
      {shap.map((contribution) => {
        const width = Math.round((Math.abs(contribution.contribution) / maxMagnitude) * 100);
        const positive = contribution.contribution >= 0;
        return (
          <div key={contribution.feature} className="flex flex-col gap-1">
            <div className="flex items-baseline justify-between text-xs">
              <span className="font-medium text-text-primary">
                {contribution.rank}. {contribution.feature}
              </span>
              <span className={positive ? "text-primary" : "text-text-secondary"}>
                {positive ? "+" : ""}
                {formatNumber(contribution.contribution, 3)}
              </span>
            </div>
            <div className="h-1.5 w-full overflow-hidden rounded-full bg-background" role="img"
              aria-label={`${contribution.feature} contribution ${contribution.contribution}`}
            >
              <div
                className="h-full rounded-full"
                style={{
                  width: `${width}%`,
                  backgroundColor: positive ? "#00D4AA" : "#8A8A9A",
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}