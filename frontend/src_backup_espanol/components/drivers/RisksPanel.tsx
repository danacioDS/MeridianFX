/**
 * Risks panel — presentational only.
 *
 * Mockup "⚠️ KEY RISKS". Renders DriversResponse.risks and
 * DriversResponse.event_sensitivity verbatim as two lists.
 */
import { NotAvailable } from "../common/NotAvailable";

interface RisksPanelProps {
  /** Risks from DriversResponse.risks. */
  risks: string[] | null;
  /** Event sensitivities from DriversResponse.event_sensitivity. */
  eventSensitivity: Array<{ event: string; impact: string }> | null;
}

export function RisksPanel({ risks, eventSensitivity }: RisksPanelProps): JSX.Element {
  if (!risks && !eventSensitivity) {
    return (
      <NotAvailable
        feature="key-risks"
        reason="UNSUPPORTED_BY_CONTRACT: risks / event sensitivities not produced"
      />
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <ListSection title="Key Risks" items={risks} emptyLabel="No risks reported." />
      <EventSensitivitySection items={eventSensitivity} />
    </div>
  );
}

function ListSection({
  title,
  items,
  emptyLabel,
}: {
  title: string;
  items: string[] | null;
  emptyLabel: string;
}): JSX.Element {
  return (
    <div className="rounded-lg border border-border bg-surface p-4">
      <h3 className="mb-2 text-sm font-semibold text-text-primary">{title}</h3>
      {items && items.length > 0 ? (
        <ul className="list-disc space-y-1 pl-5 text-sm text-text-secondary">
          {items.map((risk, index) => (
            <li key={index}>{risk}</li>
          ))}
        </ul>
      ) : (
        <p className="text-xs text-text-secondary">{emptyLabel}</p>
      )}
    </div>
  );
}

function EventSensitivitySection({
  items,
}: {
  items: Array<{ event: string; impact: string }> | null;
}): JSX.Element {
  return (
    <div className="rounded-lg border border-border bg-surface p-4">
      <h3 className="mb-2 text-sm font-semibold text-text-primary">Event Sensitivities</h3>
      {items && items.length > 0 ? (
        <ul className="space-y-1.5 text-sm">
          {items.map((item, index) => (
            <li key={index} className="flex items-center justify-between">
              <span className="text-text-secondary">{item.event}</span>
              <span
                className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                  item.impact === "HIGH"
                    ? "bg-error/20 text-error"
                    : item.impact === "MEDIUM"
                    ? "bg-warning/20 text-warning"
                    : "bg-primary/20 text-primary"
                }`}
              >
                {item.impact}
              </span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-xs text-text-secondary">No event sensitivities reported.</p>
      )}
    </div>
  );
}
