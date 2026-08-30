/**
 * Forecast Dashboard — Con Fan Chart probabilístico
 */
import {
  ApiError,
  LoadingSpinner,
  Panel,
  UniverseSelector,
} from "../components/common";
import { RegimeStrip } from "../components/mockup";
import { MacroPanel } from "../components/macro";
import { SpotCard } from "../components/forecast/SpotCard";
import { TrendCard } from "../components/forecast/TrendCard";
import { ForecastCard } from "../components/forecast/ForecastCard";
import { FanChart } from "../components/forecast/FanChart";
import { useForecastDashboard } from "../hooks/useForecastDashboard";
import { useFanChartData, transformToFanChartData } from "../hooks/useFanChartData";
import {
  useRanking,
  useActivePair,
  pairUniverseFromRanking,
  useMacroContext,
} from "../hooks";

export function ForecastPage(): JSX.Element {
  const { pair, setPair } = useActivePair();
  const ranking = useRanking();
  const { data, isLoading, error, refetch } = useForecastDashboard(pair);
  const { data: forecastData } = useFanChartData(pair);
  const macro = useMacroContext();
  const universe = pairUniverseFromRanking(ranking.data);

  if (isLoading) {
    return <LoadingSpinner label={`Cargando forecast para ${pair}...`} />;
  }

  if (error) {
    return (
      <ApiError
        message={error?.message}
        onRetry={() => void refetch()}
      />
    );
  }

  if (!data) {
    return <div>No hay datos disponibles</div>;
  }

  const { spot, trends, forecasts, volatility, source, last_date, macro: macroData } = data;

  // Preparar datos para Fan Chart
  const fanChartData = forecastData 
    ? transformToFanChartData(forecastData, spot.price, last_date)
    : [];

  return (
    <section className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-2xl font-semibold text-ink">{pair} · Forecast Dashboard</h2>
        <UniverseSelector currencies={universe} selected={pair} onChange={setPair} />
      </div>

      <RegimeStrip regime="UNKNOWN" vix={16.8} riskAppetite={0.72} />

      {/* Macro Panel */}
      {macro.data?.macro && (
        <div className="w-full">
          <MacroPanel macro={macro.data.macro} isLoading={macro.isLoading} />
        </div>
      )}

      {/* Spot Price */}
      <Panel title="📊 Precio Actual">
        <SpotCard spot={spot} pair={pair} last_date={last_date} source={source} />
      </Panel>

      {/* Tendencias */}
      {trends && (
        <Panel title="📈 Tendencias">
          <div className="space-y-2">
            <div className="text-sm text-muted">Retornos por período</div>
            <TrendCard trends={trends} />
            <div className="text-sm text-muted mt-2">
              Volatilidad anualizada: <span className="font-semibold">{volatility}%</span>
            </div>
          </div>
        </Panel>
      )}

      {/* Fan Chart */}
      <Panel title="📊 Probabilistic Forecast">
        <FanChart 
          data={fanChartData}
          currentPrice={spot.price}
          currentDate={last_date}
          title={`${pair} · 90-Day Probabilistic Forecast`}
        />
      </Panel>

      {/* Forecasts */}
      {forecasts && (
        <Panel title="🔮 Predicción XGBoost">
          <div className="space-y-3">
            <div className="text-sm text-muted">Forecast a 30, 60 y 90 días</div>
            <ForecastCard forecasts={forecasts} currentPrice={spot.price} />
            <div className="text-xs text-muted mt-2">
              Modelo: XGBoost v2.1 · Features: 37 · Horizonte: 30/60/90 días
            </div>
          </div>
        </Panel>
      )}

      {/* Análisis Macro */}
      {macroData && macroData.summary && (
        <Panel title="🏛️ Contexto Macro">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {macroData.summary.fed_funds && (
              <div className="text-center p-2 bg-panel-2 rounded">
                <div className="text-xs text-muted">Fed Funds</div>
                <div className="text-sm font-bold">{macroData.summary.fed_funds}%</div>
              </div>
            )}
            {macroData.summary.inflation && (
              <div className="text-center p-2 bg-panel-2 rounded">
                <div className="text-xs text-muted">Inflación</div>
                <div className="text-sm font-bold">{macroData.summary.inflation}%</div>
              </div>
            )}
            {macroData.summary.gdp_growth && (
              <div className="text-center p-2 bg-panel-2 rounded">
                <div className="text-xs text-muted">PIB</div>
                <div className={`text-sm font-bold ${macroData.summary.gdp_growth > 0 ? 'text-bull' : 'text-bear'}`}>
                  {macroData.summary.gdp_growth > 0 ? '+' : ''}{macroData.summary.gdp_growth}%
                </div>
              </div>
            )}
            {macroData.summary.yield_spread !== undefined && macroData.summary.yield_spread !== null && (
              <div className="text-center p-2 bg-panel-2 rounded">
                <div className="text-xs text-muted">Spread 10-2</div>
                <div className={`text-sm font-bold ${macroData.summary.yield_spread > 0 ? 'text-bull' : 'text-bear'}`}>
                  {macroData.summary.yield_spread}%
                </div>
              </div>
            )}
          </div>
          {macroData.indicators?.monetary_stance && (
            <div className="flex gap-2 mt-2 flex-wrap">
              <span className={`px-2 py-0.5 text-xs rounded-full ${macroData.indicators.monetary_stance === 'RESTRICTIVE' ? 'bg-bear/20 text-bear' : macroData.indicators.monetary_stance === 'ACCOMMODATIVE' ? 'bg-bull/20 text-bull' : 'bg-panel-3 text-muted'}`}>
                Política: {macroData.indicators.monetary_stance}
              </span>
              {macroData.indicators.growth_signal && (
                <span className={`px-2 py-0.5 text-xs rounded-full ${macroData.indicators.growth_signal === 'STRONG' ? 'bg-bull/20 text-bull' : macroData.indicators.growth_signal === 'WEAK' ? 'bg-bear/20 text-bear' : 'bg-panel-3 text-muted'}`}>
                  Crecimiento: {macroData.indicators.growth_signal}
                </span>
              )}
              {macroData.indicators.inflation_signal && (
                <span className={`px-2 py-0.5 text-xs rounded-full ${macroData.indicators.inflation_signal === 'HIGH' ? 'bg-bear/20 text-bear' : macroData.indicators.inflation_signal === 'LOW' ? 'bg-bull/20 text-bull' : 'bg-panel-3 text-muted'}`}>
                  Inflación: {macroData.indicators.inflation_signal}
                </span>
              )}
            </div>
          )}
        </Panel>
      )}
    </section>
  );
}
