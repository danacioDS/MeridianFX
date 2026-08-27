/**
 * RAG panel — presentational only.
 *
 * Mockup "🗣 POLICY SIGNALS". Renders Fed / BoJ sentiment score and expectation
 * gap from DriversResponse.rag verbatim.
 */
import type { Rag, RagSignal } from "../../types/contracts";
import { formatNumber, formatPercent } from "../../utils";
import { NotAvailable } from "../common/NotAvailable";

interface RagPanelProps {
  /** RAG signals from DriversResponse.rag. */
  rag: Rag | null;
}

export function RagPanel({ rag }: RagPanelProps): JSX.Element {
  if (!rag) {
    return (
      <NotAvailable
        feature="policy-signals"
        reason="UNSUPPORTED_BY_CONTRACT: rag signals not produced (drivers payload absent)"
      />
    );
  }

  return (
    <div className="grid grid-cols-2 gap-4">
      {(
        [
          ["Fed", rag.fed],
          ["BoJ", rag.boj],
        ] as Array<[string, RagSignal]>
      ).map(([bank, signal]) => (
        <div key={bank} className="flex flex-col gap-2 rounded-lg border border-border bg-surface p-4">
          <span className="text-sm font-semibold text-text-primary">{bank}</span>
          <div className="flex items-baseline justify-between text-xs">
            <span className="text-text-secondary">Sentiment</span>
            <span className="font-medium text-text-primary">{formatNumber(signal.sentiment, 2)}</span>
          </div>
          <div className="flex items-baseline justify-between text-xs">
            <span className="text-text-secondary">Expectation gap</span>
            <span className="font-medium text-text-primary">
              {formatPercent(signal.expectation_gap)}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}