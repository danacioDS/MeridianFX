/**
 * Loading state indicator.
 */
export function LoadingSpinner({ label = "Loading" }: { label?: string }): JSX.Element {
  return (
    <div role="status" aria-label={label} className="flex items-center gap-3 text-text-secondary">
      <span
        aria-hidden="true"
        className="h-5 w-5 animate-spin rounded-full border-2 border-primary border-t-transparent"
      />
      <span className="text-sm">{label}…</span>
    </div>
  );
}