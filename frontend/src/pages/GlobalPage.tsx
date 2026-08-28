import {
  ApiError,
  LoadingSpinner,
  NotAvailable,
  Panel,
  UniverseSelector,
} from "../components/common";
import { RegimeStrip } from "../components/mockup";
import { EarlyWarnings, RankingCard } from "../components/global";
import { useRanking, useActivePair, pairUniverseFromRanking, useDrivers } from "../hooks";

export function GlobalPage(): JSX.Element {
  const { pair, setPair } = useActivePair();
  const ranking = useRanking();
  const drivers = useDrivers(pair);
  const universe = pairUniverseFromRanking(ranking.data);

  const macroRegime = drivers.data?.macro_regime;
  const regimeLabel = macroRegime?.risk ?? 'UNKNOWN';

  if (ranking.isLoading) {
    return <LoadingSpinner label="Loading ranking" />;
  }

  if (ranking.isError) {
    return (
      <ApiError message={ranking.error?.message} onRetry={() => void ranking.refetch()} />
    );
  }

  const data = ranking.data;

  return (
    <section className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-xl font-semibold text-ink">Global Intelligence</h2>
        <UniverseSelector currencies={universe} selected={pair} onChange={setPair} />
      </div>

      {/* Regime Strip */}
      <RegimeStrip 
        regime={regimeLabel}
        vix={16.8}
        riskAppetite={0.72}
      />

      {data ? (
        <div className="flex flex-col gap-6">
          <div className="grid gap-6 lg:grid-cols-3">
            <div className="flex flex-col gap-4 lg:col-span-2">
              <Panel title="Top Opportunities">
                <RankingSummary data={data} />
                <div className="flex flex-col gap-3">
                  {data.opportunities.map((opportunity) => (
                    <RankingCard 
                      key={opportunity.pair} 
                      rank={opportunity.rank} 
                      opportunity={opportunity} 
                    />
                  ))}
                </div>
              </Panel>
            </div>

            <aside className="flex flex-col gap-4">
              <Panel title="Market Regime">
                <NotAvailable
                  feature="Market Regime"
                  reason="UNSUPPORTED_BY_CONTRACT: no RegimeResponse stream (G4)."
                />
              </Panel>
              <Panel title="Early Warnings">
                <EarlyWarnings />
              </Panel>
              <Panel title="Key Events Today">
                <NotAvailable
                  feature="key-events"
                  reason="UNSUPPORTED_BY_CONTRACT: economic calendar gap (EC-1)"
                />
              </Panel>
            </aside>
          </div>
        </div>
      ) : null}
    </section>
  );
}

function RankingSummary({ data }: { data: NonNullable<ReturnType<typeof useRanking>["data"]> }): JSX.Element {
  return (
    <dl className="flex flex-wrap gap-x-6 gap-y-1 text-sm">
      <div className="flex items-baseline gap-1.5">
        <dt className="text-xs text-muted">Top Opportunity</dt>
        <dd className="font-medium text-ink">
          {data.top_opportunity?.pair ?? "—"}
        </dd>
      </div>
      <div className="flex items-baseline gap-1.5">
        <dt className="text-xs text-muted">Actionable</dt>
        <dd className="font-medium text-ink">
          {data.total_actionable}/{data.total_pairs}
        </dd>
      </div>
    </dl>
  );
}
