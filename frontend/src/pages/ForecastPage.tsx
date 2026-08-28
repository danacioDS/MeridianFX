/**
 * Forecast Dashboard — composition layer.
 *
 * Composes useForecast / useStatus with the Prompt X forecast components.
 * No calculation occurs here: the direction, probability, return, intervals,
 * and decision fields come from the ForecastResponse contract and are passed
 * to presentational components via props.
 */
import { ApiError, LoadingSpinner, Panel, UniverseSelector } from "../components/common";
import { EconomicFilter, ForecastHero, ProbabilityChart, SignalValidity } from "../components/forecast";
import {
  pairUniverseFromRanking,
  useActivePair,
  useForecast,
  useRanking,
  useStatus,
} from "../hooks";

export function ForecastPage(): JSX.Element {
  const { pair, setPair } = useActivePair();
  const ranking = useRanking();
  const forecast = useForecast(pair);
  const status = useStatus();
  const universe = pairUniverseFromRanking(ranking.data);

  if (forecast.isLoading) {
    return <LoadingSpinner label="Loading forecast" />;
  }

  if (forecast.isError) {
    return <ApiError message={forecast.error?.message} onRetry={() => void forecast.refetch()} />;
  }

  const data = forecast.data ?? null;

  return (
    <section aria-label="Forecast Dashboard" className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-xl font-semibold text-text-primary">
          {pair} · Forecast Dashboard
        </h2>
        <UniverseSelector currencies={universe} selected={pair} onChange={setPair} />
      </div>

      <ForecastHero
        forecast={data}
        modelVersion={data?.lineage?.model?.version ?? null}
      />

      <div className="grid gap-6 lg:grid-cols-2">
        <Panel title="Economic Filter">
          <EconomicFilter decision={data?.decision ?? null} />
        </Panel>
        <Panel title="Signal Validity">
          <SignalValidity
            decisionValidity={status.data?.intelligence.decision_validity ?? null}
          />
        </Panel>
      </div>

      <Panel title="Forecast Probability">
        <ProbabilityChart data={null} />
      </Panel>
    </section>
  );
}