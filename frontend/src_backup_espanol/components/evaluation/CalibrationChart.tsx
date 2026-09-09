/**
 * Calibration chart — chart NOT AVAILABLE (series gap).
 *
 * Mockup "🎯 CALIBRATION". The contract exposes only the scalar ECE
 * (statistical.ece); there is NO calibration curve / reliability series in
 * Layer 1 §7.4 (gap CA). A distribution plot requires the missing series →
 * the chart renders NotAvailable. The ECE scalar is the only presentable datum.
 */
import { formatPercent } from "../../utils";
import { NotAvailable } from "../common/NotAvailable";

interface CalibrationChartProps {
  /** Expected calibration error scalar (performance.statistical.ece). */
  ece?: number | null;
}

export function CalibrationChart({ ece }: CalibrationChartProps): JSX.Element {
  if (ece == null) {
    return <NotAvailable feature="calibration-chart" reason="UNSUPPORTED_BY_CONTRACT: ECE absent" />;
  }

  return (
    <div className="flex flex-col gap-3 rounded-lg border border-border bg-surface p-5">
      <div className="flex items-baseline justify-between">
        <h3 className="text-sm font-semibold text-text-primary">Calibration</h3>
        <span className="text-sm text-text-secondary">
          ECE <span className="font-medium text-text-primary">{formatPercent(ece)}</span>
        </span>
      </div>
      <NotAvailable
        feature="calibration-curve"
        reason="UNSUPPORTED_BY_CONTRACT: reliability series not exposed in Layer 1 §7.4 (gap CA)"
      />
    </div>
  );
}