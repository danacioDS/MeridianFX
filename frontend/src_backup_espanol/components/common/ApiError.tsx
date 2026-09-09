/**
 * API error state.
 *
 * Displays a transport/API error with a retry action. Analytical data is never
 * transformed here — the error is presented as received from the backend client.
 */
interface ApiErrorProps {
  /** Human-readable error message (transport-level). */
  message?: string;
  /** Handler invoked when the user requests a retry. */
  onRetry?: () => void;
}

export function ApiError({ message, onRetry }: ApiErrorProps): JSX.Element {
  return (
    <div
      role="alert"
      className="flex flex-col items-start gap-2 rounded-lg border border-error bg-surface p-6"
    >
      <p className="text-sm font-semibold text-text-primary">Request failed</p>
      {message ? (
        <p className="text-sm text-text-secondary">{message}</p>
      ) : (
        <p className="text-sm text-text-secondary">
          The backend could not be reached. Your data was not modified.
        </p>
      )}
      {onRetry ? (
        <button
          type="button"
          onClick={onRetry}
          className="mt-2 rounded border border-border bg-background px-4 py-2 text-sm text-text-primary hover:border-primary"
        >
          Retry
        </button>
      ) : null}
    </div>
  );
}