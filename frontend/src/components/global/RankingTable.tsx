/**
 * RankingTable — Top opportunities ranking.
 *
 * ⚠️  Presentational ONLY. All values come from the backend /v1/fx/ranking.
 *     No returns are derived. No costs are assumed. UP/DOWN are the raw
 *     direction values provided by the backend.
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
      <div className="text-sm text-ink-soft py-6 text-center">
        No opportunities available
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      {/* Summary stats */}
      <div className="flex flex-wrap items-center gap-4 text-sm text-muted pb-3 border-b border-line">
        <span>
          Top: <b className="text-ink">{topOpportunity?.pair || "—"}</b>
        </span>
        <span>
          Score:{" "}
          <b className="text-meridian font-mono">
            {topOpportunity?.opportunity_score
              ? Math.round(topOpportunity.opportunity_score * 100)
              : 0}
            %
          </b>
        </span>
        <span>
          Actionable:{" "}
          <b className="text-ink">
            {totalActionable}/{totalPairs}
          </b>
        </span>
        <span className="ml-auto text-xs text-muted font-mono">
          {timestamp ? new Date(timestamp).toLocaleTimeString() : "—"}
        </span>
      </div>

      {/* Table */}
      <div className="border border-line rounded-xl overflow-hidden">
        <div className="grid grid-cols-[0.4fr_1fr_0.8fr_0.6fr_0.6fr_0.9fr] items-center px-4 py-2.5 text-[10.5px] uppercase tracking-wider text-muted bg-panel-2 border-b border-line font-semibold">
          <span>#</span>
          <span>Par</span>
          <span>Señal</span>
          <span>Score</span>
          <span>Edge</span>
          <span>Estado</span>
        </div>

        {opportunities.map((opp) => {
          const isUp = opp.direction === "UP";
          const scorePercent = Math.round((opp.opportunity_score || 0) * 100);
          const edge = opp.edge_ratio || 0;
          const isActionable = opp.actionable;

          return (
            <div
              key={opp.pair}
              className={`grid grid-cols-[0.4fr_1fr_0.8fr_0.6fr_0.6fr_0.9fr] items-center px-4 py-3 text-sm border-t border-line hover:bg-panel/50 transition-colors ${
                isActionable ? "bg-bull-soft/10" : ""
              }`}
            >
              <span className="font-mono text-muted text-xs font-semibold">
                #{opp.rank}
              </span>
              <span className="font-semibold text-ink">{opp.pair}</span>
              <span
                className={`text-sm font-semibold flex items-center gap-1.5 ${
                  isUp ? "text-bull" : "text-bear"
                }`}
              >
                {isUp ? "▲" : "▼"} {isUp ? "Alcista" : "Bajista"}
              </span>
              <span className="font-mono text-ink-soft">{scorePercent}%</span>
              <span className="font-mono text-ink-soft">
                {edge.toFixed(2)}x
              </span>
              <span>
                {isActionable ? (
                  <span className="text-xs px-2.5 py-1 rounded-full bg-bull-soft text-bull font-semibold">
                    Accionable
                  </span>
                ) : (
                  <span className="text-xs px-2.5 py-1 rounded-full bg-panel-2 text-muted font-semibold">
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
