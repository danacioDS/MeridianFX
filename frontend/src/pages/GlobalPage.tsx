/**
 * Global Intelligence — FASE 2: Mejora Visual
 * Sin emojis, regime strip navy, más campo visual
 */
import {
  ApiError,
  LoadingSpinner,
  Panel,
  UniverseSelector,
  MetricsHelp,
} from "../components/common";
import { RankingTable, EarlyWarnings } from "../components/global";
import { RegimeStrip } from "../components/mockup";
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
      <ApiError 
        message={ranking.error?.message} 
        onRetry={() => void ranking.refetch()} 
      />
    );
  }

  const data = ranking.data;
  const topPair = data?.top_opportunity?.pair || 'GBP/USD';

  return (
    <section className="flex flex-col gap-6">
      {/* Header con Universe Selector */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-2xl font-semibold text-ink">Global Intelligence</h2>
        <UniverseSelector currencies={universe} selected={pair} onChange={setPair} />
      </div>

      {/* Regime Strip - color navy como mockup */}
      <RegimeStrip 
        regime={regimeLabel}
        vix={16.8}
        riskAppetite={0.72}
      />

      {/* Grid principal - full width sin sidebar */}
      <div className="w-full">
        <Panel title={`Top Opportunities (${data?.total_pairs || 0} pares)`}>
          <RankingTable
            opportunities={data?.opportunities || []}
            topOpportunity={data?.top_opportunity}
            totalActionable={data?.total_actionable}
            totalPairs={data?.total_pairs}
            timestamp={data?.timestamp}
          />
        </Panel>
      </div>

      {/* Grid de 2 columnas: System Status + Early Warnings + Key Events */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* System Status */}
        <Panel title="System Status">
          <div className="space-y-2.5 text-sm">
            <div className="flex justify-between items-center border-b border-line pb-2.5">
              <span className="text-sm text-muted">Modelos activos</span>
              <span className="font-mono font-semibold text-bull text-base">9/9</span>
            </div>
            <div className="flex justify-between items-center border-b border-line pb-2.5">
              <span className="text-sm text-muted">Pares analizados</span>
              <span className="font-mono font-semibold text-base">{data?.total_pairs || 0}</span>
            </div>
            <div className="flex justify-between items-center border-b border-line pb-2.5">
              <span className="text-sm text-muted">Accionables</span>
              <span className="font-mono font-semibold text-base">{data?.total_actionable || 0}</span>
            </div>
            <div className="flex justify-between items-center pt-1">
              <span className="text-sm text-muted">Top opportunity</span>
              <span className="font-mono font-semibold text-meridian text-base">
                {data?.top_opportunity?.pair || '—'}
              </span>
            </div>
            <div className="mt-3 p-3 bg-panel-2 rounded-lg text-sm">
              <span className="text-muted text-xs">Última actualización</span>
              <span className="font-mono block text-base font-medium">
                {data?.timestamp ? new Date(data.timestamp).toLocaleTimeString() : '—'}
              </span>
            </div>
          </div>
        </Panel>

        {/* Early Warnings */}
        <Panel title="Early Warnings">
          <EarlyWarnings />
        </Panel>

        {/* Key Events */}
        <Panel title="Key Events Today">
          <div className="space-y-2.5 text-sm">
            <div className="flex items-center gap-3 text-ink-soft">
              <span className="font-mono text-sm text-bear flex-shrink-0 font-semibold">14:00</span>
              <span className="text-sm">FOMC Minutes Release</span>
            </div>
            <div className="flex items-center gap-3 text-ink-soft border-t border-line pt-2.5">
              <span className="font-mono text-sm text-amber flex-shrink-0 font-semibold">08:30</span>
              <span className="text-sm">US Durable Goods Orders</span>
            </div>
          </div>
        </Panel>
      </div>

      {/* Actionability Note */}
      <div className="actionability-note">
        <b>Actionability = f(Net Return, Minimum Edge, Probability, Costs, Regime)</b> — el umbral mínimo de edge no es fijo: varía por par según liquidez y costos de transacción.
      </div>

      {/* Metrics Help - más grande */}
      <MetricsHelp pair={topPair} />
    </section>
  );
}
