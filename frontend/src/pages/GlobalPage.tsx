/**
 * Global Intelligence — composition layer.
 *
 * Composes data hooks (useRanking) with the Prompt X presentational
 * components. No analysis, ranking, or derivation occurs here — the ranking
 * order, scores, and actionability come from the backend contract.
 * Unsupported mockup panels (Market Regime on the global view, Early Warnings,
 * Key Events) render their availability state per MIGRATION_REPORT.md.
 */
import {
  ApiError,
  LoadingSpinner,
  NotAvailable,
  Panel,
  RegimeBar,
  UniverseSelector,
} from "../components/common";
import { EarlyWarnings, RankingCard } from "../components/global";
import { useRanking, useActivePair, pairUniverseFromRanking } from "../hooks";

export function GlobalPage(): JSX.Element {
  const { pair, setPair } = useActivePair();
  const ranking = useRanking();
  const universe = pairUniverseFromRanking(ranking.data);

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
    <section aria-label="Global Intelligence" className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-xl font-semibold text-text-primary">Global Intelligence</h2>
        <UniverseSelector currencies={universe} selected={pair} onChange={setPair} />
      </div>

      {data ? (
        <div className="flex flex-col gap-6">
          <div className="grid gap-6 lg:grid-cols-3">
            <div className="flex flex-col gap-4 lg:col-span-2">
              <Panel title="Top Opportunities">
                <RankingSummary data={data} />
                <div className="flex flex-col gap-3">
                  {data.opportunities.map((opportunity) => (
                    <RankingCard key={opportunity.pair} rank={opportunity.rank} opportunity={opportunity} />
                  ))}
                </div>
              </Panel>
            </div>

            <aside className="flex flex-col gap-4">
              <Panel title="Market Regime">
                <RegimeBar macroRegime={null} />
              </Panel>
              <Panel title="Early Warnings">
                <EarlyWarnings />
              </Panel>
              <Panel title="Key Events Today">
                <NotAvailable
                  feature="key-events"
                  reason="UNSUPPORTED_BY_CONTRACT: economic calendar gap (EC-1) — no events stream in Layer 1 §7"
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
        <dt className="text-xs text-text-secondary">Top Opportunity</dt>
        <dd className="font-medium text-text-primary">
          {data.top_opportunity?.pair ?? "—"}
        </dd>
      </div>
      <div className="flex items-baseline gap-1.5">
        <dt className="text-xs text-text-secondary">Actionable</dt>
        <dd className="font-medium text-text-primary">
          {data.total_actionable}/{data.total_pairs}
        </dd>
      </div>
    </dl>
  );
}
