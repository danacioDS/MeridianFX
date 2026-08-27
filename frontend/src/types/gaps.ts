/**
 * Contract gap metadata (frontend-only infrastructure).
 *
 * Mirrors docs/Contract/CONTRACT_GAPS.md. Every entry in CONTRACT_GAP_MAP is a
 * feature that is UNSUPPORTED_BY_CONTRACT and MUST render as NOT_AVAILABLE.
 * NO_FALLBACK_ALLOWED and NO_DERIVATION_ALLOWED are hard constants: the frontend
 * MUST NOT substitute supported fields for gap fields.
 */

/** Contract support status of a feature. */
export const CONTRACT_STATUS = {
  SUPPORTED: "SUPPORTED",
  UNSUPPORTED_BY_CONTRACT: "UNSUPPORTED_BY_CONTRACT",
} as const;

/** Union type of supported contract statuses. */
export type ContractStatus =
  | typeof CONTRACT_STATUS.SUPPORTED
  | typeof CONTRACT_STATUS.UNSUPPORTED_BY_CONTRACT;

/** Feature availability state rendered to the user. */
export const FEATURE_STATE = {
  AVAILABLE: "AVAILABLE",
  NOT_AVAILABLE: "NOT_AVAILABLE",
} as const;

/** Union type of feature states. */
export type FeatureState = typeof FEATURE_STATE.AVAILABLE | typeof FEATURE_STATE.NOT_AVAILABLE;

/** Hard guard: unsupported features MUST NOT fall back to alternative rendering. */
export const NO_FALLBACK_ALLOWED = true;

/** Hard guard: unsupported features MUST NOT be derived from adjacent fields. */
export const NO_DERIVATION_ALLOWED = true;

/**
 * Closed registry of contract gaps. Key = feature name; value = reason
 * referencing docs/Contract/CONTRACT_GAPS.md. Feature availability is read from
 * this registry only — never computed from adjacent fields.
 */
export const CONTRACT_GAP_MAP: Record<string, string> = {
  getForecastHistory:
    "UNSUPPORTED_BY_CONTRACT: no forecast history response structure in Layer 1 v5.1 §7. G1.",
  useForecastHistory:
    "UNSUPPORTED_BY_CONTRACT: no forecast history response structure in Layer 1 v5.1 §7. G1.",
  getHealth:
    "UNSUPPORTED_BY_CONTRACT: no HealthResponse structure in Layer 1 v5.1 §7. G2.",
  position_size_recommendation:
    "UNSUPPORTED_BY_CONTRACT: field absent from Layer 1 v5.1 §7. G3. Use decision.position_size (supported).",
  regime:
    "UNSUPPORTED_BY_CONTRACT: no RegimeResponse structure in Layer 1 v5.1 §7. G4.",
  economic_calendar:
    "UNSUPPORTED_BY_CONTRACT: no contract field/endpoint in Layer 1 v5.1 §7. G5.",
};