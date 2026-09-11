/**
 * MarketPage — Pair analysis (price + forecast).
 *
 * v2.4 Sprint 4.5
 *
 * Consumes:
 *   - GET /v1/fx/{pair}/price?period=1y   → usePrice
 *   - GET /v1/fx/{pair}/forecast-dashboard → useForecastDashboard
 *
 * ⚠️ Types come from the hooks (useForecastDashboard) and types/ (PriceResponse).
 * ⚠️ forecast-dashboard.expected_return is already expressed in %.
 * ⚠️ No analytical values are computed here.
 */

import {
  ApiError,
  LoadingSpinner,
  EmptyState,
  Panel,
  UniverseSelector,
} from "../components/common";

import { SpotCard } from "../components/forecast/SpotCard";
import { TrendCard } from "../components/forecast/TrendCard";
import { ForecastCard } from "../components/forecast/ForecastCard";

import {
  MarketHero,
  HistoricalChart,
  MarketMeta,
} from "../components/market";

import {
  useActivePair,
  useRanking,
  usePrice,
  useForecastDashboard,
  pairUniverseFromRanking,
} from "../hooks";

import type { ForecastDashboard } from "../hooks/useForecastDashboard";
import type { PriceResponse } from "../types";


// ─── Component ────────────────────────────────────────────────────

export function MarketPage(): JSX.Element {
  const { pair, setPair } = useActivePair();
  const ranking = useRanking();

  const universe = pairUniverseFromRanking(ranking.data);

  const priceQuery = usePrice(pair, "1y");
  const dashQuery = useForecastDashboard(pair);

  if (ranking.isLoading || priceQuery.isLoading || dashQuery.isLoading) {
    return (
      <LoadingSpinner
        label={`Loading market data for ${pair}...`}
      />
    );
  }

  if (ranking.isError) {
    return (
      <ApiError
        message={ranking.error?.message}
        onRetry={() => ranking.refetch()}
      />
    );
  }

  if (priceQuery.isError || dashQuery.isError) {
    const error = priceQuery.error || dashQuery.error;

    return (
      <ApiError
        message={error?.message}
        onRetry={() => {
          void priceQuery.refetch();
          void dashQuery.refetch();
        }}
      />
    );
  }

  const dashboard =
    dashQuery.data as ForecastDashboard | undefined;

  const price =
    priceQuery.data as PriceResponse | undefined;

  if (!dashboard) {
    return (
      <EmptyState
        title="No market data available"
        message={pair}
      />
    );
  }

  return (
    <section className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-2xl font-semibold text-ink">
            📊 Market
          </h2>

          <p className="text-sm text-muted mt-1">
            {pair} · Price and forecast
          </p>
        </div>

        <UniverseSelector
          currencies={universe}
          selected={pair}
          onChange={setPair}
        />
      </div>

      {/* Spot */}
      <SpotCard
        spot={dashboard.spot}
        pair={pair}
        last_date={
          price?.last_date ??
          dashboard.as_of.slice(0, 10)
        }
        source={price?.source ?? "N/A"}
      />

      {/* Trend */}
      <TrendCard trends={dashboard.trends} />

      {/* Primary 30d forecast */}
      <MarketHero
        forecast={dashboard.forecasts["30d"]}
        horizon="30d"
      />

      {/* Forecast horizon comparison */}
      <Panel title="🔮 Forecasts (30d / 60d / 90d)">
        <ForecastCard
          forecasts={dashboard.forecasts}
          currentPrice={dashboard.spot.price}
        />
      </Panel>

      {/* Historical price */}
      {price && price.history.length > 0 && (
        <Panel title="📈 Historical Price">
          <HistoricalChart
            history={price.history}
            pair={pair}
            currentPrice={price.current_price}
          />
        </Panel>
      )}

      {/* Data provenance */}
      <MarketMeta
        asOf={dashboard.as_of}
        lastDate={price?.last_date}
        source={price?.source}
        freshness={price?.freshness}
        volatility={dashboard.volatility}
      />
    </section>
  );
}
