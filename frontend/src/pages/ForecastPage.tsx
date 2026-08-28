import { ApiError, LoadingSpinner, Panel, UniverseSelector } from "../components/common";
import { EconomicFilter, ForecastHero, ProbabilityChart, SignalValidity } from "../components/forecast";
import { Gauge, PipelineStepper, RegimeStrip } from "../components/mockup";
import {
  pairUniverseFromRanking,
  useActivePair,
  useForecast,
  useRanking,
  useStatus,
  useDrivers,
} from "../hooks";

export function ForecastPage(): JSX.Element {
  const { pair, setPair } = useActivePair();
  const ranking = useRanking();
  const forecast = useForecast(pair);
  const status = useStatus();
  const drivers = useDrivers(pair);
  const universe = pairUniverseFromRanking(ranking.data);

  if (forecast.isLoading) {
    return <LoadingSpinner label="Loading forecast" />;
  }

  if (forecast.isError) {
    return <ApiError message={forecast.error?.message} onRetry={() => void forecast.refetch()} />;
  }

  const data = forecast.data ?? null;
  const decision = data?.decision;
  const prediction = data?.prediction;

  const direction = prediction?.direction ?? 'UP';
  const probability = prediction?.probability ?? 0.5;
  const netReturn = decision?.net_return ?? 0;
  const edgeRatio = decision?.edge_ratio ?? 0;
  const actionable = decision?.actionable ?? false;
  const confidence = decision?.confidence ?? 0;

  const macroRegime = drivers.data?.macro_regime;
  const regimeLabel = macroRegime?.risk ?? 'UNKNOWN';

  return (
    <section className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-xl font-semibold text-ink">
          {pair} · Forecast Dashboard
        </h2>
        <UniverseSelector currencies={universe} selected={pair} onChange={setPair} />
      </div>

      <RegimeStrip 
        regime={regimeLabel}
        vix={16.8}
        riskAppetite={0.72}
      />

      <PipelineStepper
        direction={direction}
        probability={probability}
        netReturn={netReturn}
        edgeRatio={edgeRatio}
        actionable={actionable}
        confidence={confidence}
      />

      <div className="grid gap-6 lg:grid-cols-2">
        <div>
          <ForecastHero
            forecast={data}
            modelVersion={data?.lineage?.model?.version ?? null}
          />
        </div>
        <div className="flex items-center justify-center border border-line rounded-xl bg-panel p-6">
          <Gauge probability={probability} label="Probabilidad calibrada" size="large" />
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Panel title="Economic Filter">
          <EconomicFilter decision={decision ?? null} />
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
