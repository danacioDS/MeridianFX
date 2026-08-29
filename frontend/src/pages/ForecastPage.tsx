/**
 * Forecast Dashboard — Contract-driven con todos los componentes presentacionales
 * Mantiene toda la UX de v2.3.0-macro-panel: UniverseSelector, Ranking, MacroPanel, RegimeStrip
 */
import {
  ApiError,
  LoadingSpinner,
  Panel,
  UniverseSelector,
} from "../components/common";
import { RegimeStrip } from "../components/mockup";
import { MacroPanel } from "../components/macro";
import { ForecastHero } from "../components/forecast/ForecastHero";
import { ProbabilityGauge } from "../components/forecast/ProbabilityGauge";
import { ProbabilityChart } from "../components/forecast/ProbabilityChart";
import { EconomicFilter } from "../components/forecast/EconomicFilter";
import { SignalValidity } from "../components/forecast/SignalValidity";
import {
  useForecast,
  useRanking,
  useActivePair,
  pairUniverseFromRanking,
  useInterpretation,
  useMacroContext,
} from "../hooks";

export function ForecastPage(): JSX.Element {
  const { pair, setPair } = useActivePair();
  const ranking = useRanking();
  const forecast = useForecast(pair);
  const interpretation = useInterpretation(pair);
  const macro = useMacroContext();
  const universe = pairUniverseFromRanking(ranking.data);

  if (forecast.isLoading) {
    return <LoadingSpinner label={`Cargando forecast para ${pair}...`} />;
  }

  if (forecast.isError) {
    return (
      <ApiError
        message={forecast.error?.message}
        onRetry={() => void forecast.refetch()}
      />
    );
  }

  const data = forecast.data;
  const prediction = data?.prediction;
  const decision = data?.decision;
  const drivers = data?.drivers;
  const data_quality = data?.data_quality;
  const interpretationData = interpretation.data;
  const macroData = macro.data;

  return (
    <section className="flex flex-col gap-6">
      {/* Header con selector de par */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-2xl font-semibold text-ink">{pair} · Forecast Dashboard</h2>
        <UniverseSelector currencies={universe} selected={pair} onChange={setPair} />
      </div>

      {/* Regime Strip (mockup) */}
      <RegimeStrip regime="UNKNOWN" vix={16.8} riskAppetite={0.72} />

      {/* Macro Panel - primera fila */}
      {macroData?.macro && (
        <div className="w-full">
          <MacroPanel macro={macroData.macro} isLoading={macro.isLoading} />
        </div>
      )}

      {/* Forecast Hero - usa el contrato completo */}
      {data && (
        <div className="w-full">
          <ForecastHero forecast={data} />
        </div>
      )}

      {/* Probability Gauge + Economic Filter */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <Panel title="Probability">
            <ProbabilityGauge probability={prediction?.probability} />
          </Panel>
        </div>
        <div className="lg:col-span-2">
          <EconomicFilter decision={decision ?? null} />
        </div>
      </div>

      {/* Probability Chart + Signal Validity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ProbabilityChart data={null} />
        <SignalValidity decisionValidity={null} />
      </div>

      {/* Economic Interpretation */}
      {interpretationData && (
        <Panel title="📝 Economic Interpretation">
          <div className="prose prose-sm max-w-none">
            <p className="text-gray-700">{interpretationData.summary}</p>
            {interpretationData.bullets && (
              <ul className="list-disc pl-4 space-y-1">
                {interpretationData.bullets.map((bullet: string, i: number) => (
                  <li key={i} className="text-gray-600">{bullet}</li>
                ))}
              </ul>
            )}
          </div>
        </Panel>
      )}

      {/* Key Drivers */}
      {drivers && drivers.shap && drivers.shap.length > 0 && (
        <Panel title="🔍 Key Drivers">
          <div className="space-y-3">
            {drivers.shap.slice(0, 6).map((driver) => (
              <div
                key={`${driver.rank}-${driver.feature}`}
                className="flex justify-between items-center p-2 bg-gray-50 rounded"
              >
                <span className="text-sm font-medium">{driver.feature}</span>
                <span className={`text-sm ${driver.contribution > 0 ? 'text-bull' : driver.contribution < 0 ? 'text-bear' : 'text-text-secondary'}`}>
                  {driver.contribution > 0 ? '+' : ''}{driver.contribution.toFixed(3)}
                </span>
              </div>
            ))}
          </div>
        </Panel>
      )}

      {/* Data Quality */}
      {data_quality && (
        <Panel title="📊 Data Quality">
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <div className="text-sm text-gray-500">Overall</div>
              <div className="font-semibold">{data_quality.overall.toFixed(2)}</div>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-500">Status</div>
              <div className="font-semibold">{data_quality.status}</div>
            </div>
          </div>
        </Panel>
      )}
    </section>
  );
}
