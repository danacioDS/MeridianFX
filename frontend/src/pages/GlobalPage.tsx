/**
 * Global Page — Selector de moneda + precio + gráfico + forecast + ranking
 * Inspirado en SignalIQ
 */
import { Panel, UniverseSelector, LoadingSpinner, ApiError } from "../components/common";
import { RegimeStrip } from "../components/mockup";
import { RankingTable } from "../components/global/RankingTable";
import { PriceChartSignalIQ } from "../components/global/PriceChartSignalIQ";
import { useRanking, useActivePair, pairUniverseFromRanking } from "../hooks";
import { useForecastDashboard } from "../hooks/useForecastDashboard";

export function GlobalPage(): JSX.Element {
  const { pair, setPair } = useActivePair();
  const ranking = useRanking();
  const dashboard = useForecastDashboard(pair);
  const universe = pairUniverseFromRanking(ranking.data);

  if (ranking.isLoading || dashboard.isLoading) {
    return <LoadingSpinner label={`Cargando datos para ${pair}...`} />;
  }

  if (ranking.isError) {
    return <ApiError message={ranking.error?.message} onRetry={() => ranking.refetch()} />;
  }

  if (dashboard.isError) {
    return <ApiError message={dashboard.error?.message} onRetry={() => dashboard.refetch()} />;
  }

  const rankingData = ranking.data;
  const data = dashboard.data;

  // Extraer datos para RankingTable
  const opportunities = rankingData?.opportunities || [];
  const topOpportunity = opportunities.length > 0 ? opportunities[0] : null;
  const totalActionable = opportunities.filter((o: any) => o.actionable).length;
  const totalPairs = opportunities.length;

  return (
    <section className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-2xl font-semibold text-ink">🌍 Global Intelligence</h2>
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted">{universe.length} pares</span>
          <UniverseSelector currencies={universe} selected={pair} onChange={setPair} />
        </div>
      </div>

      <RegimeStrip regime="UNKNOWN" vix={16.8} riskAppetite={0.72} />

      {/* Detalle de la moneda seleccionada */}
      {data && (
        <>
          {/* Precio Actual + Gráfico */}
          <Panel title={`📊 ${pair} · Precio y Cotización`}>
            <div className="space-y-4">
              {/* Cabecera de precio */}
              <div className="flex flex-wrap items-center justify-between p-4 bg-panel-2 rounded-lg border border-line">
                <div>
                  <div className="text-sm text-muted">{pair}</div>
                  <div className="text-3xl font-bold text-ink">{data.spot.price.toFixed(4)}</div>
                  <div className="text-xs text-muted">Fuente: {data.source} · {data.last_date}</div>
                </div>
                <div className="text-right">
                  <div className={`text-2xl font-bold ${data.spot.change_pct >= 0 ? 'text-bull' : 'text-bear'}`}>
                    {data.spot.change_pct >= 0 ? '▲' : '▼'} {data.spot.change_pct >= 0 ? '+' : ''}{data.spot.change_pct.toFixed(2)}%
                  </div>
                  <div className={`text-sm ${data.spot.change_pct >= 0 ? 'text-bull' : 'text-bear'}`}>
                    {data.spot.change_pct >= 0 ? '+' : ''}{data.spot.change_abs.toFixed(4)}
                  </div>
                  <div className="text-xs text-muted">vs día anterior</div>
                  <div className="text-xs text-muted mt-1">
                    Predicción: <span className={data.forecasts?.["30d"]?.direction === 'UP' ? 'text-bull' : 'text-bear'}>
                      {data.forecasts?.["30d"]?.direction === 'UP' ? '▲ Alcista' : '▼ Bajista'}
                    </span> ({ (data.forecasts?.["30d"]?.probability || 0.5) * 100 }%)
                  </div>
                </div>
              </div>

              {/* Gráfico interactivo con hover */}
              <PriceChartSignalIQ
                history={data.history || []}
                currentPrice={data.spot.price}
                pair={pair}
              />
            </div>
          </Panel>

          {/* Forecast 30/60/90 días */}
          {data.forecasts && (
            <Panel title="🔮 Predicción XGBoost">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {["30d", "60d", "90d"].map((h) => {
                  const f = data.forecasts[h as keyof typeof data.forecasts];
                  if (!f) return null;
                  const isUp = f.direction === "UP";
                  const targetPrice = data.spot.price * (1 + f.expected_return / 100);
                  return (
                    <div key={h} className="p-4 bg-panel-2 rounded-lg border border-line">
                      <div className="text-xs text-muted">{h}</div>
                      <div className={`text-xl font-bold ${isUp ? 'text-bull' : 'text-bear'}`}>
                        {isUp ? '▲' : '▼'} {f.expected_return}%
                      </div>
                      <div className="text-sm text-ink-soft">Confianza: {(f.probability * 100).toFixed(1)}%</div>
                      <div className="text-xs text-muted mt-1">
                        Precio: {targetPrice.toFixed(4)}
                      </div>
                      <div className="text-xs text-muted">
                        IC 95%: {f.ci_95_lower.toFixed(4)} — {f.ci_95_upper.toFixed(4)}
                      </div>
                    </div>
                  );
                })}
              </div>
              <div className="text-xs text-muted mt-2">
                Modelo: XGBoost v2.1 · Features: 37
              </div>
            </Panel>
          )}

          {/* Contexto Macro */}
          {data.macro && data.macro.summary && (
            <Panel title="🏛️ Contexto Macro">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {data.macro.summary.fed_funds && (
                  <div className="text-center p-2 bg-panel-2 rounded">
                    <div className="text-xs text-muted">Fed Funds</div>
                    <div className="text-sm font-bold">{data.macro.summary.fed_funds}%</div>
                  </div>
                )}
                {data.macro.summary.inflation && (
                  <div className="text-center p-2 bg-panel-2 rounded">
                    <div className="text-xs text-muted">Inflación</div>
                    <div className="text-sm font-bold">{data.macro.summary.inflation}%</div>
                  </div>
                )}
                {data.macro.summary.gdp_growth && (
                  <div className="text-center p-2 bg-panel-2 rounded">
                    <div className="text-xs text-muted">PIB</div>
                    <div className={`text-sm font-bold ${data.macro.summary.gdp_growth > 0 ? 'text-bull' : 'text-bear'}`}>
                      {data.macro.summary.gdp_growth > 0 ? '+' : ''}{data.macro.summary.gdp_growth}%
                    </div>
                  </div>
                )}
                {data.macro.summary.yield_spread !== undefined && data.macro.summary.yield_spread !== null && (
                  <div className="text-center p-2 bg-panel-2 rounded">
                    <div className="text-xs text-muted">Spread 10-2</div>
                    <div className={`text-sm font-bold ${data.macro.summary.yield_spread > 0 ? 'text-bull' : 'text-bear'}`}>
                      {data.macro.summary.yield_spread}%
                    </div>
                  </div>
                )}
              </div>
              {data.macro.indicators?.monetary_stance && (
                <div className="flex gap-2 mt-2 flex-wrap">
                  <span className={`px-2 py-0.5 text-xs rounded-full ${
                    data.macro.indicators.monetary_stance === 'RESTRICTIVE' ? 'bg-bear/20 text-bear' :
                    data.macro.indicators.monetary_stance === 'ACCOMMODATIVE' ? 'bg-bull/20 text-bull' :
                    'bg-panel-3 text-muted'
                  }`}>
                    Política: {data.macro.indicators.monetary_stance}
                  </span>
                  {data.macro.indicators.growth_signal && (
                    <span className={`px-2 py-0.5 text-xs rounded-full ${
                      data.macro.indicators.growth_signal === 'STRONG' ? 'bg-bull/20 text-bull' :
                      data.macro.indicators.growth_signal === 'WEAK' ? 'bg-bear/20 text-bear' :
                      'bg-panel-3 text-muted'
                    }`}>
                      Crecimiento: {data.macro.indicators.growth_signal}
                    </span>
                  )}
                  {data.macro.indicators.inflation_signal && (
                    <span className={`px-2 py-0.5 text-xs rounded-full ${
                      data.macro.indicators.inflation_signal === 'HIGH' ? 'bg-bear/20 text-bear' :
                      data.macro.indicators.inflation_signal === 'LOW' ? 'bg-bull/20 text-bull' :
                      'bg-panel-3 text-muted'
                    }`}>
                      Inflación: {data.macro.indicators.inflation_signal}
                    </span>
                  )}
                </div>
              )}
            </Panel>
          )}
        </>
      )}

      {/* Ranking de oportunidades */}
      {rankingData && (
        <Panel title="📈 Top Opportunities">
          <RankingTable
            opportunities={opportunities}
            topOpportunity={topOpportunity}
            totalActionable={totalActionable}
            totalPairs={totalPairs}
            timestamp={rankingData.snapshot_timestamp}
          />
        </Panel>
      )}
    </section>
  );
}
