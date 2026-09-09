/**
 * Actionable Info — Explicación de qué significa "Actionable" y la fórmula estadística
 */

interface ActionableInfoProps {
  threshold?: {
    minEdge: number;
    minNetReturn: number;
    minProbability: number;
  };
}

export function ActionableInfo({ 
  threshold = { minEdge: 1.5, minNetReturn: 0.001, minProbability: 0.6 }
}: ActionableInfoProps): JSX.Element {
  return (
    <div className="rounded-lg border border-border bg-surface p-5 mt-4">
      <h4 className="text-sm font-semibold text-text-primary mb-3">
        📊 ¿Qué significa "Actionable"?
      </h4>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
        {/* Columna 1: Definición */}
        <div className="bg-panel-2 rounded-lg p-4">
          <div className="text-xs text-muted uppercase tracking-wider mb-2">Definición</div>
          <p className="text-text-primary leading-relaxed">
            Una oportunidad es <span className="text-bull font-semibold">actionable</span> 
            cuando el <strong>edge neto</strong> (beneficio esperado después de costes) 
            supera el umbral mínimo definido por el sistema.
          </p>
          <p className="text-text-secondary text-xs mt-2">
            No basta con tener una dirección probable; la oportunidad debe ser 
            <strong> económicamente atractiva</strong> después de considerar costes de transacción, 
            slippage y comisiones.
          </p>
        </div>

        {/* Columna 2: Fórmula */}
        <div className="bg-panel-2 rounded-lg p-4">
          <div className="text-xs text-muted uppercase tracking-wider mb-2">Fórmula Estadística</div>
          <div className="font-mono text-xs text-text-primary space-y-1">
            <div><span className="text-muted">1. Gross Return =</span> Expected Return</div>
            <div><span className="text-muted">2. Net Return =</span> Gross - Spread - Slippage - Fees</div>
            <div><span className="text-muted">3. Edge Ratio =</span> |Net Return| / Volatility</div>
            <div><span className="text-muted">4. Actionable =</span> Edge Ratio ≥ {threshold.minEdge} <span className="text-muted">AND</span> Net Return &gt; 0</div>
          </div>
          <div className="mt-2 text-xs text-muted border-t border-border pt-2">
            <span className="font-mono">Volatility</span> = Desviación estándar anualizada de retornos
          </div>
        </div>

        {/* Columna 3: Teoría */}
        <div className="bg-panel-2 rounded-lg p-4">
          <div className="text-xs text-muted uppercase tracking-wider mb-2">Base Teórica</div>
          <p className="text-text-primary leading-relaxed">
            El concepto de <strong>edge</strong> proviene de la teoría de decisiones bajo incertidumbre. 
            Una señal con alta probabilidad (ej: 70%) <span className="text-bear font-semibold">no es suficiente</span> 
            si el beneficio esperado no compensa el riesgo y los costes.
          </p>
          <p className="text-text-secondary text-xs mt-2">
            Referencia: <span className="font-mono">Sharpe Ratio, Kelly Criterion, Transaction Cost Analysis</span>
          </p>
          <div className="mt-2 flex items-center gap-2 text-xs">
            <span className="text-bull">✅ Pasa:</span>
            <span className="text-text-secondary">Edge ≥ {threshold.minEdge}</span>
            <span className="text-bear ml-2">❌ No pasa:</span>
            <span className="text-text-secondary">Edge &lt; {threshold.minEdge}</span>
          </div>
        </div>
      </div>

      {/* Umbrales actuales */}
      <div className="mt-3 pt-3 border-t border-border text-xs text-muted flex flex-wrap gap-4">
        <div>🔹 <span className="text-text-primary">Umbral Edge Mínimo:</span> {threshold.minEdge}x</div>
        <div>🔹 <span className="text-text-primary">Umbral Net Return:</span> &gt; {threshold.minNetReturn * 100}%</div>
        <div>🔹 <span className="text-text-primary">Umbral Probabilidad:</span> &gt; {threshold.minProbability * 100}%</div>
        <div>💡 <span className="text-text-primary">Interpretación:</span> "Sin edge" = no supera los umbrales</div>
      </div>
    </div>
  );
}
