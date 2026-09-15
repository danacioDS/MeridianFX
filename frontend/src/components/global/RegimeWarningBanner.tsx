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
      ? "RÉGIMEN ADMINISTRADO"
      : "FLOTACIÓN GESTIONADA"
    : "RÉGIMEN NO VERIFICADO";

  const description = isManaged
    ? "La clasificación del sistema indica que este par no opera bajo una flotación completamente libre. Las predicciones direccionales deben interpretarse con cautela."
    : "El régimen cambiario de este par no está verificado por el sistema. La divergencia estadística no demuestra por sí sola intervención ni un régimen administrado.";

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
                Divergencia actual respecto a flotación limpia:{" "}
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
