/**
 * MarketPage — Pair analysis (price + forecast).
 *
 * ⚠️ PLACEHOLDER — to be implemented in Sprint 4.
 */
import {
  Panel,
  UniverseSelector,
} from "../components/common";
import {
  useActivePair,
  useRanking,
  pairUniverseFromRanking,
} from "../hooks";

export function MarketPage(): JSX.Element {
  const { pair, setPair } = useActivePair();
  const ranking = useRanking();
  const universe = pairUniverseFromRanking(ranking.data);

  return (
    <section className="flex flex-col gap-6">
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

      <Panel title="Coming soon">
        <p className="text-sm text-muted">
          Price chart, forecast, probability, and expected path
          will be integrated here in Sprint 4.
        </p>
      </Panel>
    </section>
  );
}
