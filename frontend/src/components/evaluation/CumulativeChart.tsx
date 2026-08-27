/**
 * Cumulative return chart — NOT AVAILABLE (series gap).
 *
 * Mockup "📈 CUMULATIVE RETURN". Layer 1 §7.4 exposes only single-period
 * economic metrics (total_return) — there is NO historical return series in any
 * contract (gap). Rendering a time-series without the series would fabricate
 * data → NotAvailable.
 */
import { NotAvailable } from "../common/NotAvailable";

export function CumulativeChart(): JSX.Element {
  return (
    <NotAvailable
      feature="cumulative-return-chart"
      reason="UNSUPPORTED_BY_CONTRACT: no historical return series in Layer 1 §7.4"
    />
  );
}