/**
 * Drivers & Explanation — composition layer.
 *
 * Composes useDrivers with the Prompt X drivers components. SHAP drivers,
 * macro regime, RAG signals, narrative, risks, and event sensitivities are
 * passed through verbatim — this page never derives new drivers or values.
 */
import { ApiError, LoadingSpinner, Panel, UniverseSelector } from "../components/common";
import { MacroRegime, NarrativePanel, RagPanel, RisksPanel, ShapBars } from "../components/drivers";
import { pairUniverseFromRanking, useActivePair, useDrivers, useRanking } from "../hooks";

export function DriversPage(): JSX.Element {
  const { pair, setPair } = useActivePair();
  const ranking = useRanking();
  const drivers = useDrivers(pair);
  const universe = pairUniverseFromRanking(ranking.data);

  if (drivers.isLoading) {
    return <LoadingSpinner label="Loading drivers" />;
  }

  if (drivers.isError) {
    return <ApiError message={drivers.error?.message} onRetry={() => void drivers.refetch()} />;
  }

  const data = drivers.data ?? null;

  return (
    <section aria-label="Drivers & Explanation" className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-xl font-semibold text-text-primary">
          {pair} · Drivers &amp; Explanation
        </h2>
        <UniverseSelector currencies={universe} selected={pair} onChange={setPair} />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Panel title="Key Drivers">
          <ShapBars shap={data?.shap ?? null} />
        </Panel>

        <Panel title="Macro Regime">
          <MacroRegime macroRegime={data?.macro_regime ?? null} />
        </Panel>

        <Panel title="Policy Signals (Fed vs BoJ)">
          <RagPanel rag={data?.rag ?? null} />
        </Panel>

        <Panel title="Executive Narrative">
          <NarrativePanel narrative={data?.narrative ?? null} />
        </Panel>

        <Panel title="Risks & Event Sensitivities">
          <RisksPanel risks={data?.risks ?? null} eventSensitivity={data?.event_sensitivity ?? null} />
        </Panel>
      </div>
    </section>
  );
}