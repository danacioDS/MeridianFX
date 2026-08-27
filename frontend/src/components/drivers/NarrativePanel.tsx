/**
 * Narrative panel — presentational only.
 *
 * Mockup "🧠 EXECUTIVE NARRATIVE". Renders DriversResponse.narrative verbatim.
 * Layer 3 owns narrative generation — this component only presents it.
 */
import { NotAvailable } from "../common/NotAvailable";

interface NarrativePanelProps {
  /** Executive narrative from DriversResponse.narrative. */
  narrative: string | null;
}

export function NarrativePanel({ narrative }: NarrativePanelProps): JSX.Element {
  if (!narrative) {
    return (
      <NotAvailable
        feature="executive-narrative"
        reason="UNSUPPORTED_BY_CONTRACT: narrative not produced (drivers payload absent)"
      />
    );
  }

  return (
    <div className="rounded-lg border border-border bg-surface p-5 text-sm leading-relaxed text-text-primary">
      {narrative}
    </div>
  );
}