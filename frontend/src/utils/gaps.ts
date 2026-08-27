/**
 * Contract gap helpers (presentation/infrastructure).
 *
 * Feature availability is read ONLY from the closed CONTRACT_GAP_MAP registry
 * (see types/gaps.ts and docs/Contract/CONTRACT_GAPS.md). Availability is never
 * inferred. NO_FALLBACK_ALLOWED and NO_DERIVATION_ALLOWED are hard constants.
 */
import { CONTRACT_GAP_MAP, FEATURE_STATE, type FeatureState } from "../types/gaps";

/** Returns true when a feature is UNSUPPORTED_BY_CONTRACT. */
export function isUnsupported(feature: string): boolean {
  return Object.prototype.hasOwnProperty.call(CONTRACT_GAP_MAP, feature);
}

/** Returns the feature state (NOT_AVAILABLE for unsupported features). */
export function getFeatureState(feature: string): FeatureState {
  return isUnsupported(feature) ? FEATURE_STATE.NOT_AVAILABLE : FEATURE_STATE.AVAILABLE;
}

export { CONTRACT_GAP_MAP };