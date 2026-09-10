/**
 * Formats a value already expressed in percentage points.
 *
 * Example:
 *   -0.78 -> "-0.78%"
 *
 * Unlike formatPercent(), this function does NOT multiply by 100.
 * It is intentionally local to the Market domain because
 * forecast-dashboard.expected_return is already expressed in %.
 */
export function formatPercentRaw(
  value: number | null | undefined,
  decimals: number = 2
): string {
  if (value == null) return "N/A";
  return `${value.toFixed(decimals)}%`;
}
