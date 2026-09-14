/**
 * Actionable Info — Explicación de qué significa "Actionable" y la fórmula estadística.
 *
 * ⚠️  Presentational ONLY. No thresholds are hardcoded. If the backend does not
 *     provide requiredMinimumEdge, the component renders an "unavailable" state
 *     instead of inventing values.
 */

interface ActionableInfoProps {
  /** Required minimum edge ratio from the backend. Null/undefined → unavailable. */
  requiredMinimumEdge?: number | null;
}

export function ActionableInfo({
  requiredMinimumEdge,
}: ActionableInfoProps): JSX.Element {
  const hasEvaluation = requiredMinimumEdge != null;

  return (
    <div className="rounded-lg border border-border bg-surface p-5 mt-4">
      <h4 className="text-sm font-semibold text-text-primary mb-3">
        📊 ¿Qué significa "Actionable"?
      </h4>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
        {/* Columna 1: Definición */}
        <div className="bg-panel-2 rounded-lg p-4">
          <div className="text-xs text-muted uppercase tracking-wider mb-2">
            Definición
          </div>
          <p className="text-text-primary leading-relaxed">
            Una oportunidad es{" "}
            <span className="text-bull font-semibold">actionable</span> cuando
            el <strong>edge neto</strong> (beneficio esperado después de costes)
            supera el umbral mínimo definido por el sistema.
          </p>
          <p className="text-text-secondary text-xs mt-2">
            No basta con tener una dirección probable; la oportunidad debe ser{" "}
            <strong>económicamente atractiva</strong> después de considerar
            costes de transacción, slippage y comisiones.
          </p>
        </div>

        {/* Columna 2: Fórmula */}
        <div className="bg-panel-2 rounded-lg p-4">
          <div className="text-xs text-muted uppercase tracking-wider mb-2">
            Fórmula Estadística
          </div>
          <div className="font-mono text-xs text-text-primary space-y-1">
            <div>
              <span className="text-muted">1. Gross Return =</span> Expected
              Return
            </div>
            <div>
              <span className="text-muted">2. Net Return =</span> Gross - Spread
              - Slippage - Fees
            </div>
            <div>
              <span className="text-muted">3. Edge Ratio =</span> Net Return /
              Required Minimum Edge
            </div>
            <div>
              <span className="text-muted">4. Actionable when:</span>{" "}
              Edge Ratio ≥ 1.0 <span className="text-muted">AND</span> all hard gates pass
            </div>
          </div>
          <div className="mt-2 text-xs text-muted border-t border-border pt-2">
            <span className="font-mono">Volatility</span> = Desviación estándar
            anualizada de retornos
          </div>
        </div>

        {/* Columna 3: Teoría */}
        <div className="bg-panel-2 rounded-lg p-4">
          <div className="text-xs text-muted uppercase tracking-wider mb-2">
            Base Teórica
          </div>
          <p className="text-text-primary leading-relaxed">
            El concepto de <strong>edge</strong> proviene de la teoría de
            decisiones bajo incertidumbre. Una señal con alta probabilidad (ej:
            70%) <span className="text-bear font-semibold">no es suficiente</span>{" "}
            si el beneficio esperado no compensa el riesgo y los costes.
          </p>
          <p className="text-text-secondary text-xs mt-2">
            Referencia:{" "}
            <span className="font-mono">
              Sharpe Ratio, Kelly Criterion, Transaction Cost Analysis
            </span>
          </p>
          {hasEvaluation && (
            <div className="mt-2 flex items-center gap-2 text-xs">
              <span className="text-bull">✅ Actionable:</span>
              <span className="text-text-secondary">
                Edge Ratio ≥ 1.0
              </span>
              <span className="text-bear ml-2">❌ Not actionable:</span>
              <span className="text-text-secondary">
                Edge Ratio &lt; 1.0
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Umbrales o estado unavailable */}
      <div className="mt-3 pt-3 border-t border-border text-xs text-muted flex flex-wrap gap-4">
        {hasEvaluation ? (
          <>
            <div>
              🔹 <span className="text-text-primary">Required Minimum Edge:</span>{" "}
              {requiredMinimumEdge.toFixed(2)} bps
            </div>
            <div>
              💡 <span className="text-text-primary">Interpretación:</span>{" "}
              Edge Ratio &lt; 1.0 means Net Return is below the required minimum.
            </div>
          </>
        ) : (
          <div className="w-full">
            <div>
              ℹ️{" "}
              <span className="text-text-primary">
                No economic evaluation is available for this pair.
              </span>
            </div>
            <div className="mt-1 text-[11px]">
              The backend did not provide the minimum required edge, so no
              default value is shown. See the Model divergence notice for context.
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
