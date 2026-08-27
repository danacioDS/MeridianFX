/**
 * Ranking table card — presentational only.
 *
 * Mockup "TOP OPPORTUNITIES". Receives the ranked opportunities array from
 * RankingResponse.opportunities (ordered by Layer 2). Renders rank, pair,
 * direction arrow (visually maps the direction field), opportunity score,
 * edge ratio, and the backend actionability flag. The "NET / SIGNAL / EXPECTED
 * RETURN" secondary line is NOT contractual — parent passes null -> NotAvailable.
 */
import type { RankedOpportunity } from "../../types/contracts";
import { formatDirection, formatEdgeRatio, formatNumber, getDirectionArrow } from "../../utils";
import { NotAvailable } from "../common/NotAvailable";

interface RankingCardProps {
  /** Rank position (backend-provided). */
  rank: number;
  /** A single ranked opportunity. */
  opportunity: RankedOpportunity;
  /** Secondary details — render only when a parent supplies contract fields. */
  secondaryLine?: string | null;
}

export function RankingCard({
  rank,
  opportunity,
  secondaryLine,
}: RankingCardProps): JSX.Element {
  const actionable = opportunity.actionable;
  const direction = formatDirection(opportunity.direction);
  const arrow = getDirectionArrow(opportunity.direction);

  return (
    <div className="flex flex-col gap-2 rounded-lg border border-border bg-background p-4">
      <div className="flex items-center justify-between gap-3">
        <span className="text-lg font-bold text-text-secondary">#{rank}</span>
        <span className="text-base font-semibold text-text-primary">{opportunity.pair}</span>
        <span className="flex items-center gap-1 text-sm font-medium text-text-primary">
          <span aria-hidden="true">{arrow}</span>
          {direction}
        </span>
        <span className="text-sm text-text-secondary">
          Score {formatNumber(opportunity.opportunity_score, 2)}
        </span>
        <span className="text-sm text-text-secondary">
          Edge {formatEdgeRatio(opportunity.edge_ratio)}
        </span>
        <StatusPill actionable={actionable} />
      </div>

      {secondaryLine ? (
        <p className="text-xs text-text-secondary">{secondaryLine}</p>
      ) : (
        <NotAvailable feature="opportunity secondary details" reason="UNSUPPORTED_BY_CONTRACT" />
      )}
    </div>
  );
}

function StatusPill({ actionable }: { actionable: boolean }): JSX.Element {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ${
        actionable
          ? "bg-primary/15 text-primary"
          : "border border-border text-text-secondary"
      }`}
      aria-label={actionable ? "Actionable" : "Not actionable"}
    >
      <span
        aria-hidden="true"
        className="inline-block h-1.5 w-1.5 rounded-full"
        style={{ backgroundColor: actionable ? "#00D4AA" : "#8A8A9A" }}
      />
      <span className={actionable ? "" : "text-text-secondary"}>
        {actionable ? "Actionable" : "No edge"}
      </span>
    </span>
  );
}