import { ApiError, LoadingSpinner, Panel, UniverseSelector } from "../components/common";
import { MacroRegime, NarrativePanel, RagPanel, RisksPanel } from "../components/drivers";
import { SHAPBar, RegimeStrip } from "../components/mockup";
import {
  pairUniverseFromRanking,
  useActivePair,
  useDrivers,
  useRanking,
} from "../hooks";

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
  
  const shapContributions = data?.shap?.map((item, index) => ({
    feature: item.feature,
    contribution: item.contribution,
    rank: index + 1
  })) ?? [];

  const macroRegime = data?.macro_regime;
  const regimeLabel = macroRegime?.risk ?? 'UNKNOWN';

  return (
    <section className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-xl font-semibold text-ink">
          {pair} · Drivers &amp; Explanation
        </h2>
        <UniverseSelector currencies={universe} selected={pair} onChange={setPair} />
      </div>

      <RegimeStrip 
        regime={regimeLabel}
        vix={16.8}
        riskAppetite={0.72}
      />

      <div className="grid gap-6 lg:grid-cols-2">
        <Panel title="Key Drivers (SHAP)">
          <SHAPBar contributions={shapContributions} maxContributions={10} />
          <div className="mt-3 text-xs text-muted font-mono">
            Model: xgb-v1.0 · Source: DriversResponse
          </div>
        </Panel>

        <Panel title="Macro Regime">
          <MacroRegime macroRegime={macroRegime ?? null} />
        </Panel>

        <Panel title="Policy Signals (Fed vs BoJ)">
          <RagPanel rag={data?.rag ?? null} />
        </Panel>

        <Panel title="Executive Narrative">
          <NarrativePanel narrative={data?.narrative ?? null} />
        </Panel>

        <Panel title="Risks & Event Sensitivities" className="lg:col-span-2">
          <RisksPanel 
            risks={data?.risks ?? null} 
            eventSensitivity={data?.event_sensitivity ?? null} 
          />
        </Panel>
      </div>
    </section>
  );
}
