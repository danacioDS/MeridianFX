/**
 * RegimeWarningBanner — Exchange-regime context for divergence analysis.
 *
 * Only asserts a managed/administered regime when the backend explicitly
 * classifies it as such. UNKNOWN is presented as uncertainty, not as proof
 * of intervention or market management.
 */
interface RegimeWarningBannerProps {
  regime: string;
  interpretation: string;
  zscore: number | null;
}

export function RegimeWarningBanner({
  regime,
  interpretation,
  zscore,
}: RegimeWarningBannerProps): JSX.Element | null {
  if (regime === "free_float") {
    return null;
  }

  const isManaged =
    regime === "administered" || regime === "managed_float";

  const regimeLabel = isManaged
    ? regime === "administered"
      ? "MANAGED REGIME"
      : "MANAGED FLOAT"
    : "REGIME NOT VERIFIED";

  const description = isManaged
    ? "The system classifies this pair as not operating under a fully free float. Directional forecasts should be interpreted with caution."
    : "The exchange regime of this pair is not verified by the system. Statistical divergence alone does not prove intervention or a managed regime.";

  return (
    <div
      className={`mb-4 rounded-lg border-2 px-4 py-3 ${
        isManaged
          ? "border-red-500/50 bg-red-500/10"
          : "border-amber-500/40 bg-amber-500/10"
      }`}
    >
      <div className="flex items-start gap-3">
        <span
          className={`text-lg leading-none ${
            isManaged ? "text-red-400" : "text-amber-400"
          }`}
        >
          {isManaged ? "⚠" : "ⓘ"}
        </span>

        <div className="flex-1">
          <div
            className={`text-xs font-bold tracking-wider uppercase ${
              isManaged ? "text-red-300" : "text-amber-300"
            }`}
          >
            {regimeLabel}
          </div>

          <div className="mt-1 text-xs leading-relaxed text-muted">
            {description}

            {zscore !== null && (
              <>
                {" "}
                Current divergence vs clean-float baseline:{" "}
                <span className="font-mono">
                  z = {zscore.toFixed(2)} ({interpretation})
                </span>
                .
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
