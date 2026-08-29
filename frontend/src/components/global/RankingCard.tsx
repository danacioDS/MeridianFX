import type { RankedOpportunity } from "../../types/contracts";

interface RankingCardProps {
  rank: number;
  opportunity: RankedOpportunity;
}

export function RankingCard({ rank, opportunity }: RankingCardProps): JSX.Element {
  const isActionable = opportunity.actionable;
  const isUp = opportunity.direction === 'UP' as any;
  const scorePercent = Math.round((opportunity.opportunity_score || 0) * 100);
  const edge = opportunity.edge_ratio || 0;

  return (
    <div className={`flex items-center gap-4 px-4 py-3 transition-colors hover:bg-panel ${
      isActionable ? 'bg-bull-soft/10' : ''
    }`}>
      {/* Rank */}
      <span className="text-sm font-mono text-muted w-8">#{rank}</span>
      
      {/* Pair */}
      <span className="text-sm font-semibold text-ink w-20">{opportunity.pair}</span>
      
      {/* Dirección con estilo mockup */}
      <span className={`text-sm font-semibold flex items-center gap-1.5 w-24 ${
        isUp ? 'text-bull' : 'text-bear'
      }`}>
        {isUp ? '▲' : '▼'} {isUp ? 'Alcista' : 'Bajista'}
      </span>
      
      {/* Score como porcentaje */}
      <span className="text-sm font-mono text-ink-soft w-16">{scorePercent}%</span>
      
      {/* Edge Ratio */}
      <span className="text-sm font-mono text-ink-soft w-16">{edge.toFixed(2)}x</span>
      
      {/* Estado */}
      <span className="ml-auto">
        {isActionable ? (
          <span className="text-xs px-3 py-1 rounded-full bg-bull-soft text-bull font-semibold uppercase tracking-wide">
            Accionable
          </span>
        ) : (
          <span className="text-xs px-3 py-1 rounded-full bg-panel-2 text-muted font-medium uppercase tracking-wide">
            Sin edge
          </span>
        )}
      </span>
    </div>
  );
}
