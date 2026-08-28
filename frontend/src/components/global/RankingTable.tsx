/**
 * Ranking Table — presentational only.
 * 
 * Mismo estilo que ForecastHero
 */
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
    return (
      <div className="text-sm text-text-secondary py-4 text-center">
        No opportunities available
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      {/* Summary stats - igual que ForecastHero */}
      <div className="grid grid-cols-2 gap-x-6 gap-y-3 text-sm">
        <div className="flex items-baseline gap-1.5">
          <span className="text-xs text-text-secondary">Top Opportunity</span>
          <span className="font-medium text-text-primary">
            {topOpportunity?.pair ?? "—"}
          </span>
        </div>
        <div className="flex items-baseline gap-1.5">
          <span className="text-xs text-text-secondary">Score</span>
          <span className="font-mono font-medium text-[#0E7C86]">
            {topOpportunity?.opportunity_score 
              ? Math.round(topOpportunity.opportunity_score * 100) 
              : 0}%
          </span>
        </div>
        <div className="flex items-baseline gap-1.5">
          <span className="text-xs text-text-secondary">Actionable</span>
          <span className="font-mono font-medium text-text-primary">
            {totalActionable}/{totalPairs}
          </span>
        </div>
        <div className="flex items-baseline gap-1.5">
          <span className="text-xs text-text-secondary">Updated</span>
          <span className="font-mono text-xs text-text-secondary">
            {timestamp ? new Date(timestamp).toLocaleTimeString() : "—"}
          </span>
        </div>
      </div>

      {/* Tabla - igual que en ForecastHero pero con grid */}
      <div className="border border-border rounded-lg overflow-hidden">
        {/* Header */}
        <div className="grid grid-cols-[0.5fr_1.2fr_1fr_0.8fr_0.8fr_1fr] items-center px-4 py-2.5 text-[10.5px] uppercase tracking-wider text-text-secondary bg-surface-2 border-b border-border">
          <span>#</span>
          <span>Pair</span>
          <span>Signal</span>
          <span>Prob.</span>
          <span>Edge</span>
          <span>Status</span>
        </div>

        {/* Filas */}
        {opportunities.map((opp) => {
          const isUp = opp.direction === 'UP';
          const scorePercent = Math.round((opp.opportunity_score || 0) * 100);
          const edge = opp.edge_ratio || 0;
          const isActionable = opp.actionable;

          return (
            <div 
              key={opp.pair} 
              className={`grid grid-cols-[0.5fr_1.2fr_1fr_0.8fr_0.8fr_1fr] items-center px-4 py-3 text-sm border-t border-border hover:bg-surface/50 transition-colors ${
                isActionable ? 'bg-[#E7F5EE]/10' : ''
              }`}
            >
              <span className="font-mono text-text-secondary text-xs font-semibold">#{opp.rank}</span>
              <span className="font-semibold text-text-primary">{opp.pair}</span>
              <span className={`text-sm font-semibold flex items-center gap-1.5 ${isUp ? 'text-[#0E8F5F]' : 'text-[#C4453A]'}`}>
                {isUp ? '▲' : '▼'} {isUp ? 'Bullish' : 'Bearish'}
              </span>
              <span className="font-mono text-text-secondary">{scorePercent}%</span>
              <span className="font-mono text-text-secondary">{edge.toFixed(2)}x</span>
              <span>
                {isActionable ? (
                  <span className="text-xs px-2.5 py-1 rounded-full bg-[#E7F5EE] text-[#0E8F5F] font-semibold">
                    Actionable
                  </span>
                ) : (
                  <span className="text-xs px-2.5 py-1 rounded-full bg-surface-2 text-text-secondary font-semibold">
                    No edge
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
