/**
 * "Feature not available" state.
 *
 * Rendered for contract gaps. Reason defaults to UNSUPPORTED_BY_CONTRACT.
 * NO_FALLBACK_ALLOWED = true and NO_DERIVATION_ALLOWED = true: the unsupported
 * feature is never substituted with a supported field or a derived value.
 */
import { FEATURE_STATE, NO_DERIVATION_ALLOWED, NO_FALLBACK_ALLOWED } from "../../types/gaps";

interface NotAvailableProps {
  /** Feature identifier being reported unavailable. */
  feature?: string;
  /** Reason for unavailability. Defaults to UNSUPPORTED_BY_CONTRACT. */
  reason?: string;
}

export function NotAvailable({
  feature,
  reason = "UNSUPPORTED_BY_CONTRACT",
}: NotAvailableProps): JSX.Element {
  return (
    <div
      role="status"
      aria-label="Feature not available"
      className="flex flex-col items-start gap-1 rounded-lg border border-border bg-surface p-6"
    >
      <p className="text-sm font-semibold text-text-primary">Feature not available</p>
      {feature ? <p className="text-xs text-text-secondary">Feature: {feature}</p> : null}
      <p className="text-xs text-text-secondary">State: {FEATURE_STATE.NOT_AVAILABLE}</p>
      <p className="text-xs text-text-secondary">Reason: {reason}</p>
      <p className="text-xs text-text-secondary">
        No fallback allowed: {String(NO_FALLBACK_ALLOWED)}
      </p>
      <p className="text-xs text-text-secondary">
        No derivation allowed: {String(NO_DERIVATION_ALLOWED)}
      </p>
    </div>
  );
}