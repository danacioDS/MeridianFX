/**
 * Evaluation & Performance — composition layer.
 *
 * Composes usePerformance with the Prompt X evaluation components. All metrics
 * (statistical, economic, degradation, ECE) come from the PerformanceResponse
 * contract. Benchmark / calibration-curve / cumulative-series panels are
 * contract gaps and render their availability state (MIGRATION_REPORT.md §4).
 */
import { ApiError, LoadingSpinner, Panel, UniverseSelector } from "../components/common";
import {
  CalibrationChart,
  CumulativeChart,
  DriftIndicator,
  PerformanceTable,
} from "../components/evaluation";
import {
  pairUniverseFromRanking,
  PERFORMANCE_PERIODS,
  useActivePair,
  usePerformance,
  usePerformancePeriod,
  useRanking,
} from "../hooks";
import type { PerformancePeriod } from "../types";

export function EvaluationPage(): JSX.Element {
  const { pair, setPair } = useActivePair();
  const { period, setPeriod } = usePerformancePeriod();
  const ranking = useRanking();
  const performance = usePerformance(pair, period);
  const universe = pairUniverseFromRanking(ranking.data);

  if (performance.isLoading) {
    return <LoadingSpinner label="Loading performance" />;
  }

  if (performance.isError) {
    return (
      <ApiError
        message={performance.error?.message}
        onRetry={() => void performance.refetch()}
      />
    );
  }

  const data = performance.data ?? null;

  return (
    <section aria-label="Evaluation & Performance" className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-xl font-semibold text-text-primary">
          {pair} · Evaluation &amp; Performance
        </h2>
        <div className="flex items-center gap-3">
          <PeriodSelector period={period} onChange={setPeriod} />
          <UniverseSelector currencies={universe} selected={pair} onChange={setPair} />
        </div>
      </div>

      <PerformanceTable performance={data} />

      <div className="grid gap-6 lg:grid-cols-2">
        <Panel title="Calibration">
          <CalibrationChart ece={data?.statistical.ece ?? null} />
        </Panel>
        <Panel title="Model Degradation">
          <DriftIndicator degradation={data?.degradation ?? null} />
        </Panel>
      </div>

      <Panel title="Cumulative Return">
        <CumulativeChart />
      </Panel>
    </section>
  );
}

function PeriodSelector({
  period,
  onChange,
}: {
  period: PerformancePeriod;
  onChange: (next: PerformancePeriod) => void;
}): JSX.Element {
  return (
    <div role="group" aria-label="Evaluation period" className="flex items-center gap-1">
      {PERFORMANCE_PERIODS.map((option) => (
        <button
          key={option}
          type="button"
          onClick={() => onChange(option)}
          aria-pressed={option === period}
          className={`rounded border px-2.5 py-1 text-xs font-medium transition-colors ${
            option === period
              ? "border-primary bg-primary/10 text-text-primary"
              : "border-border bg-background text-text-secondary hover:border-primary"
          }`}
        >
          {option}
        </button>
      ))}
    </div>
  );
}