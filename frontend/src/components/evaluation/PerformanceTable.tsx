/**
 * Performance table — presentational only.
 *
 * Mockup "📊 MODEL PERFORMANCE" / "📈 STRATEGY PERFORMANCE". Renders the
 * statistical and economic metric blocks of PerformanceResponse verbatim.
 * The mockup columns "vs Benchmark" and "Status" have NO contract source
 * (Layer 1 §7.4 defines single-period metrics only) → rendered as
 * NotAvailable, never derived.
 */
import type { PerformanceResponse } from "../../types/contracts";
import { formatDrawdown, formatPercent, formatSharpe } from "../../utils";
import { NotAvailable } from "../common/NotAvailable";

interface PerformanceTableProps {
  /** Performance payload from /performance. */
  performance: PerformanceResponse | null;
}

export function PerformanceTable({ performance }: PerformanceTableProps): JSX.Element {
  if (!performance) {
    return (
      <NotAvailable
        feature="model-performance"
        reason="UNSUPPORTED_BY_CONTRACT: performance payload absent"
      />
    );
  }

  const statistical: Array<[string, string]> = [
    ["Directional Accuracy", formatPercent(performance.statistical.directional_accuracy)],
    ["AUC", formatPercent(performance.statistical.auc)],
    ["Brier Score", formatSharpe(performance.statistical.brier_score)],
    ["Expected Calib. Error", formatPercent(performance.statistical.ece)],
    ["Log Loss", formatSharpe(performance.statistical.log_loss)],
  ];

  const economic: Array<[string, string]> = [
    ["Sharpe Ratio", formatSharpe(performance.economic.sharpe_ratio)],
    ["Net Sharpe", formatSharpe(performance.economic.sharpe_net)],
    ["Max Drawdown", formatDrawdown(performance.economic.max_drawdown)],
    ["Profit Factor", formatSharpe(performance.economic.profit_factor)],
    ["Win Rate", formatPercent(performance.economic.win_rate)],
    ["Total Return", formatPercent(performance.economic.total_return)],
  ];

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <MetricCard title="Model Performance" rows={statistical} />
      <MetricCard title="Strategy Performance" rows={economic} />
    </div>
  );
}

function MetricCard({ title, rows }: { title: string; rows: Array<[string, string]> }): JSX.Element {
  return (
    <div className="flex flex-col gap-2 rounded-lg border border-border bg-surface p-4">
      <h3 className="text-sm font-semibold text-text-primary">{title}</h3>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border text-left text-xs text-text-secondary">
            <th className="py-1.5 pr-2 font-medium">Metric</th>
            <th className="py-1.5 pr-2 font-medium">Value</th>
            <th className="py-1.5 font-normal text-text-secondary">vs Benchmark</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(([metric, value]) => (
            <tr key={metric} className="border-b border-border/50">
              <td className="py-1.5 pr-2 text-text-primary">{metric}</td>
              <td className="py-1.5 pr-2 font-medium text-text-primary">{value}</td>
              <td className="py-1.5 text-xs text-text-secondary">—</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="text-xs text-text-secondary">
        Benchmark column: NOT in Layer 1 §7.4 — not provided, not derived.
      </p>
    </div>
  );
}