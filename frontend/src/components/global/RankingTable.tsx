import type { RankedOpportunity } from "../../types/contracts";
import { formatDirection, formatEdgeRatio, getDirectionArrow } from "../../utils";

interface RankingTableProps {
  opportunities: RankedOpportunity[];
}

export function RankingTable({ opportunities }: RankingTableProps): JSX.Element {
  if (!opportunities || opportunities.length === 0) {
    return <div className="text-muted text-sm py-4 text-center">No opportunities available</div>;
  }

  return (
    <div className="border border-line rounded-xl overflow-hidden">
      <div className="grid grid-cols-[0.5fr_1fr_0.9fr_0.7fr_0.8fr_0.8fr] items-center px-4 py-3 text-[10.5px] uppercase tracking-wider text-muted bg-panel-2 border-b border-line">
        <span>#</span>
        <span>Pair</span>
        <span>Signal</span>
        <span>Prob.</span>
        <span>Edge</span>
        <span>Status</span>
      </div>

      {opportunities.map((opp) => {
        const isActionable = opp.actionable;
        const direction = formatDirection(opp.direction);
        const arrow = getDirectionArrow(opp.direction);
        const isUp = opp.direction === 'UP';
        const probPercent = Math.round((opp.opportunity_score || 0) * 100);
        const edge = opp.edge_ratio || 0;

        return (
          <div key={opp.pair} className="grid grid-cols-[0.5fr_1fr_0.9fr_0.7fr_0.8fr_0.8fr] items-center px-4 py-3 text-sm border-b border-line last:border-b-0 hover:bg-panel/50">
            <span className="font-mono text-muted text-xs">#{opp.rank}</span>
            <span className="font-semibold text-ink">{opp.pair}</span>
            <span className={`text-sm font-semibold flex items-center gap-1 ${isUp ? 'text-bull' : 'text-bear'}`}>
              <span>{arrow}</span> {direction}
            </span>
            <span className="font-mono text-ink-soft">{probPercent}%</span>
            <span className="font-mono text-ink-soft">{edge.toFixed(2)}x</span>
            <span>
              {isActionable ? (
                <span className="text-xs px-2.5 py-1 rounded-full bg-bull-soft text-bull">Actionable</span>
              ) : (
                <span className="text-xs px-2.5 py-1 rounded-full bg-panel-2 text-muted">No edge</span>
              )}
            </span>
          </div>
        );
      })}
    </div>
  );
}
