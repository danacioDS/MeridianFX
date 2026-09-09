import type { RankedOpportunity } from "../../types/contracts";

interface RankingTableProps {
  opportunities: RankedOpportunity[];
  topOpportunity?: RankedOpportunity | null;
  totalActionable?: number;
  totalPairs?: number;
  timestamp?: string;
}

export function RankingTable({
  opportunities,
  topOpportunity,
  totalActionable = 0,
  totalPairs = 0,
  timestamp,
}: RankingTableProps): JSX.Element {
  if (!opportunities || opportunities.length === 0) {
    return <div className="text-sm text-ink-soft py-6 text-center">No opportunities available</div>;
  }

  const getReturn = (edge: number, direction: string) => {
    const baseReturn = edge * 0.3;
    const sign = direction === 'UP' as any ? 1 : -1;
    return sign * baseReturn;
  };

  const getNetReturn = (edge: number, direction: string) => {
    const gross = getReturn(edge, direction);
    const costs = 0.05;
    return gross - costs;
  };

  return (
    <div className="flex flex-col gap-4">
      {/* Summary stats - sin emojis */}
      <div className="flex flex-wrap items-center gap-4 text-sm text-muted pb-3 border-b border-line">
        <span>Top: <b className="text-ink">{topOpportunity?.pair || '—'}</b></span>
        <span>Score: <b className="text-meridian font-mono">
          {topOpportunity?.opportunity_score ? Math.round(topOpportunity.opportunity_score * 100) : 0}%
        </b></span>
        <span>Actionable: <b className="text-ink">{totalActionable}/{totalPairs}</b></span>
        <span className="ml-auto text-xs text-muted font-mono">
          {timestamp ? new Date(timestamp).toLocaleTimeString() : '—'}
        </span>
      </div>

      {/* Tabla */}
      <div className="border border-line rounded-xl overflow-hidden">
        <div className="grid grid-cols-[0.4fr_1fr_0.8fr_0.6fr_0.7fr_1.1fr_1fr] items-center px-4 py-2.5 text-[10.5px] uppercase tracking-wider text-muted bg-panel-2 border-b border-line font-semibold">
          <span>#</span>
          <span>Par</span>
          <span>Señal</span>
          <span>Prob.</span>
          <span>Edge</span>
          <span>Ret. esp. / Net</span>
          <span>Estado</span>
        </div>

        {opportunities.map((opp) => {
          const isUp = opp.direction === 'UP' as any;
          const scorePercent = Math.round((opp.opportunity_score || 0) * 100);
          const edge = opp.edge_ratio || 0;
          const isActionable = opp.actionable;
          const grossReturn = getReturn(edge, opp.direction);
          const netReturn = getNetReturn(edge, opp.direction);

          return (
            <div 
              key={opp.pair} 
              className={`grid grid-cols-[0.4fr_1fr_0.8fr_0.6fr_0.7fr_1.1fr_1fr] items-center px-4 py-3 text-sm border-t border-line hover:bg-panel/50 transition-colors ${
                isActionable ? 'bg-bull-soft/10' : ''
              }`}
            >
              <span className="font-mono text-muted text-xs font-semibold">#{opp.rank}</span>
              <span className="font-semibold text-ink">{opp.pair}</span>
              <span className={`text-sm font-semibold flex items-center gap-1.5 ${isUp ? 'text-bull' : 'text-bear'}`}>
                {isUp ? '▲' : '▼'} {isUp ? 'Alcista' : 'Bajista'}
              </span>
              <span className="font-mono text-ink-soft">{scorePercent}%</span>
              <span className="font-mono text-ink-soft">{edge.toFixed(2)}x</span>
              <div className="flex flex-col leading-tight">
                <span className={`font-mono text-xs ${grossReturn >= 0 ? 'text-bull' : 'text-bear'}`}>
                  {grossReturn >= 0 ? '+' : ''}{grossReturn.toFixed(2)}%
                </span>
                <span className="font-mono text-[10px] text-muted">
                  / Net {netReturn >= 0 ? '+' : ''}{netReturn.toFixed(2)}%
                </span>
              </div>
              <span>
                {isActionable ? (
                  <span className="text-xs px-2.5 py-1 rounded-full bg-bull-soft text-bull font-semibold">
                    Accionable
                  </span>
                ) : (
                  <span className="text-xs px-2.5 py-1 rounded-full bg-panel-2 text-muted font-semibold">
                    Sin edge
                  </span>
                )}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
