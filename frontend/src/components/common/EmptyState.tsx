/**
 * Empty state indicator.
 *
 * Rendered when a successful request returns no data.
 * Distinct from:
 *   - NotAvailable: contract gap (field doesn't exist in the contract)
 *   - ApiError: transport/network error
 */
interface EmptyStateProps {
  /** Primary message. */
  title?: string;
  /** Optional detail below the title. */
  message?: string;
  /** Optional icon/emoji. */
  icon?: string;
}

export function EmptyState({
  title = "No data available",
  message,
  icon = "○",
}: EmptyStateProps): JSX.Element {
  return (
    <div
      role="status"
      aria-label={title}
      className="flex flex-col items-center justify-center gap-2 py-8 text-center"
    >
      <span className="text-3xl text-muted">{icon}</span>
      <p className="text-sm font-semibold text-ink">{title}</p>
      {message ? <p className="text-xs text-muted">{message}</p> : null}
    </div>
  );
}
