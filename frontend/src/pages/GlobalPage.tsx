import { safeToFixed } from "../utils/safeFormat";
import {
  Panel,
  UniverseSelector,
  LoadingSpinner,
  ApiError,
} from "../components/common";
import {
  RankingTable,
  ActionableInfo,
  ModelExplanation,
  MarketIntelligenceHero,
  LeadingSignals,
} from "../components/global";
import { PriceChartSignalIQ } from "../components/global/PriceChartSignalIQ";
import {
  useRanking,
  useActivePair,
  pairUniverseFromRanking,
} from "../hooks";
import { useForecastDashboard } from "../hooks/useForecastDashboard";
import { useMarketIntelligence } from "../hooks/useMarketIntelligence";

/**
 * Global Page — Executive market intelligence overview.
 *
 * Aggregate intelligence comes directly from /v1/market-intelligence.
 * Pair-specific price and forecast data comes from forecast-dashboard.
 *
 * No financial scores, expected returns, costs, confidence, or
 * actionability are calculated in this page.
 */
export function GlobalPage(): JSX.Element {
  const { pair, setPair } = useActivePair();
  const ranking = useRanking();
  const dashboard = useForecastDashboard(pair);
  const marketIntelligence = useMarketIntelligence();

  const universe = pairUniverseFromRanking(ranking.data);

  if (
    ranking.isLoading ||
    dashboard.isLoading ||
    marketIntelligence.isLoading
  ) {
    return <LoadingSpinner label={`Cargando datos para ${pair}...`} />;
  }

  if (ranking.isError) {
    return (
      <ApiError
        message={ranking.error?.message}
        onRetry={() => ranking.refetch()}
      />
    );
  }

  if (dashboard.isError) {
    return (
      <ApiError
        message={dashboard.error?.message}
        onRetry={() => dashboard.refetch()}
      />
    );
  }

  if (marketIntelligence.isError) {
    return (
      <ApiError
        message={marketIntelligence.error?.message}
        onRetry={() => marketIntelligence.refetch()}
      />
    );
  }

  const rankingData = ranking.data;
  const data = dashboard.data;
  const intelligence = marketIntelligence.data;

  const opportunities = rankingData?.opportunities || [];
  const topOpportunity =
    opportunities.length > 0 ? opportunities[0] : null;
  const totalActionable = opportunities.filter(
    (o: any) => o.actionable
  ).length;
  const totalPairs = opportunities.length;

  return (
    <section className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-2xl font-semibold text-ink">
          🌍 Global Intelligence
        </h2>

        <div className="flex items-center gap-2">
          <span className="text-xs text-muted">
            {universe.length} pares
          </span>

          <UniverseSelector
            currencies={universe}
            selected={pair}
            onChange={setPair}
          />
        </div>
      </div>

      {/* System-wide Market Intelligence */}
      {intelligence && (
        <>
          <MarketIntelligenceHero
            status={intelligence.decision_view.status}
            marketCoverage={intelligence.current_context.market_coverage}
            actionableCount={intelligence.decision_view.actionable_count}
            totalPairs={intelligence.decision_view.total_pairs}
            summary={intelligence.summary}
          />

          <Panel title="📡 Leading Signals">
            <LeadingSignals signals={intelligence.key_signals} />
          </Panel>
        </>
      )}

      {/* Selected pair detail */}
      {data && (
        <>
          {/* Current Price + Chart */}
          <Panel title={`📊 ${pair} · Precio y Cotización`}>
            <div className="space-y-4">
              <div className="flex flex-wrap items-center justify-between p-4 bg-panel-2 rounded-lg border border-line">
                <div>
                  <div className="text-sm text-muted">{pair}</div>

                  <div className="text-3xl font-bold text-ink">
                    {safeToFixed(data.spot.price, 4)}
                  </div>

                  <div className="text-xs text-muted">
                    Fuente: {data.source} · {data.last_date}
                  </div>
                </div>

                <div className="text-right">
                  <div
                    className={`text-2xl font-bold ${
                      data.spot.change_pct >= 0
                        ? "text-bull"
                        : "text-bear"
                    }`}
                  >
                    {data.spot.change_pct >= 0 ? "▲" : "▼"}{" "}
                    {data.spot.change_pct >= 0 ? "+" : ""}
                    {safeToFixed(data.spot.change_pct, 2)}%
                  </div>

                  <div
                    className={`text-sm ${
                      data.spot.change_pct >= 0
                        ? "text-bull"
                        : "text-bear"
                    }`}
                  >
                    {data.spot.change_pct >= 0 ? "+" : ""}
                    {safeToFixed(data.spot.change_abs, 4)}
                  </div>

                  <div className="text-xs text-muted">
                    vs día anterior
                  </div>

                  <div className="text-xs text-muted mt-1">
                    Forecast:{" "}
                    <span
                      className={
                        data.forecasts?.["30d"]?.direction === "UP"
                          ? "text-bull"
                          : "text-bear"
                      }
                    >
                      {data.forecasts?.["30d"]?.direction === "UP"
                        ? "▲ Bullish"
                        : "▼ Bearish"}
                    </span>{" "}
                    ({(data.forecasts?.["30d"]?.probability || 0.5) * 100}%)
                  </div>
                </div>
              </div>

              <PriceChartSignalIQ
                history={data.history || []}
                currentPrice={data.spot.price}
                pair={pair}
              />
            </div>
          </Panel>

          {/* Forecast 30/60/90 days */}
          {data.forecasts && (
            <Panel title="🔮 Logistic_24 Forecast">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {["30d", "60d", "90d"].map((h) => {
                  const f =
                    data.forecasts[h as keyof typeof data.forecasts];

                  if (!f) return null;

                  const isUp = f.direction === "UP";

                  const targetPrice =
                    data.spot.price * (1 + f.expected_return / 100);

                  return (
                    <div
                      key={h}
                      className="p-4 bg-panel-2 rounded-lg border border-line"
                    >
                      <div className="text-xs text-muted">{h}</div>

                      <div
                        className={`text-xl font-bold ${
                          isUp ? "text-bull" : "text-bear"
                        }`}
                      >
                        {isUp ? "▲" : "▼"} {f.expected_return}%
                      </div>

                      <div className="text-sm text-ink-soft">
                        Confidence:{" "}
                        {safeToFixed(f.probability * 100, 1)}%
                      </div>

                      <div className="text-xs text-muted mt-1">
                        Precio: {safeToFixed(targetPrice, 4)}
                      </div>

                      <div className="text-xs text-muted">
                        IC 95%: {safeToFixed(f.ci_95_lower, 4)} —{" "}
                        {safeToFixed(f.ci_95_upper, 4)}
                      </div>
                    </div>
                  );
                })}
              </div>

              <div className="text-xs text-muted mt-2">
                Modelo: XGBoost v2.1 · Features: 37
              </div>

              <div className="text-xs text-muted mt-1">
                <ModelExplanation />
              </div>
            </Panel>
          )}
        </>
      )}

      {/* Ranking */}
      {rankingData && (
        <>
          <Panel title="📈 Top Opportunities — Forecast basada en Logistic Regression">
            <RankingTable
              opportunities={opportunities}
              topOpportunity={topOpportunity}
              totalActionable={totalActionable}
              totalPairs={totalPairs}
              timestamp={rankingData.timestamp}
            />
          </Panel>

          <ActionableInfo />
        </>
      )}

      <div className="text-xs text-muted mt-2">
        🔹 El ranking de oportunidades utiliza{" "}
        <strong>Logistic Regression</strong> para estimar la dirección y
        probabilidad. XGBoost se usa para el retorno esperado en el
        forecast.
      </div>
    </section>
  );
}
