/**
 * Global Intelligence — composition layer.
 * 
 * Mismo estilo que ForecastPage usando Panel y componentes presentacionales
 */
import {
  ApiError,
  LoadingSpinner,
  Panel,
  UniverseSelector,
  MetricsHelp,
} from "../components/common";
import { RankingTable } from "../components/global";
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
      {/* Header igual que Forecast */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-xl font-semibold text-text-primary">
          Global Intelligence
        </h2>
        <UniverseSelector currencies={universe} selected={pair} onChange={setPair} />
      </div>

      {/* Regime Strip */}
      <RegimeStrip 
        regime={regimeLabel}
        vix={16.8}
        riskAppetite={0.72}
      />

      {/* Grid principal igual que Forecast */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Columna principal */}
        <div className="lg:col-span-2">
          <Panel title={`Top Opportunities (${data?.total_pairs || 0} pairs)`}>
            <RankingTable
              opportunities={data?.opportunities || []}
              topOpportunity={data?.top_opportunity}
              totalActionable={data?.total_actionable}
              totalPairs={data?.total_pairs}
              timestamp={data?.timestamp}
            />
          </Panel>
        </div>

        {/* Sidebar */}
        <aside className="flex flex-col gap-4">
          {/* Estado del Sistema */}
          <Panel title="System Status">
            <div className="space-y-2 text-sm">
              <div className="flex justify-between items-center border-b border-border pb-2">
                <span className="text-text-secondary">Active models</span>
                <span className="font-mono font-semibold text-[#0E8F5F]">9/9</span>
              </div>
              <div className="flex justify-between items-center border-b border-border pb-2">
                <span className="text-text-secondary">Pairs analyzed</span>
                <span className="font-mono font-semibold">{data?.total_pairs || 0}</span>
              </div>
              <div className="flex justify-between items-center border-b border-border pb-2">
                <span className="text-text-secondary">Actionable</span>
                <span className="font-mono font-semibold">{data?.total_actionable || 0}</span>
              </div>
              <div className="flex justify-between items-center pt-1">
                <span className="text-text-secondary">Top opportunity</span>
                <span className="font-mono font-semibold text-[#0E7C86]">
                  {data?.top_opportunity?.pair || '—'}
                </span>
              </div>
            </div>
          </Panel>

          {/* Early Warnings */}
          <Panel title="Early Warnings">
            <div className="space-y-2 text-sm">
              <div className="flex items-start gap-2 text-text-secondary">
                <span className="flex-shrink-0">⚠️</span>
                <span>JPY short positioning at 1-year extreme <span className="font-mono text-xs text-text-secondary">(z-score: -2.1)</span></span>
              </div>
              <div className="flex items-start gap-2 text-text-secondary border-t border-border pt-2">
                <span className="flex-shrink-0">ℹ️</span>
                <span>Risk-on regime confirmed (VIX &lt; 18)</span>
              </div>
            </div>
          </Panel>

          {/* Key Events */}
          <Panel title="Key Events Today">
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-3 text-text-secondary">
                <span className="font-mono text-xs text-[#C4453A] flex-shrink-0">14:00</span>
                <span>FOMC Minutes Release</span>
              </div>
              <div className="flex items-center gap-3 text-text-secondary border-t border-border pt-2">
                <span className="font-mono text-xs text-[#B8860B] flex-shrink-0">08:30</span>
                <span>US Durable Goods Orders</span>
              </div>
            </div>
          </Panel>
        </aside>
      </div>

      {/* Nota de actionability */}
      <div className="text-xs text-text-secondary bg-surface border border-border rounded-lg px-4 py-3 leading-relaxed">
        <b className="font-mono text-text-primary">Actionability = f(Net Return, Minimum Edge, Probability, Costs, Regime)</b> — minimum edge threshold varies by pair based on liquidity and transaction costs.
      </div>

      {/* Cuadro de ayuda - Metrics Explanation */}
      <MetricsHelp pair={topPair} />
    </section>
  );
}
