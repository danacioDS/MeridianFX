/**
 * Model Explanation — Explica la diferencia entre XGBoost y Logistic
 */
import { useState } from 'react';

export function ModelExplanation(): JSX.Element {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="mt-2">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="text-xs text-muted hover:text-primary transition-colors flex items-center gap-1"
      >
        <span>📖</span>
        <span>{isOpen ? 'Ocultar explicación' : '¿Por qué hay dos modelos?'}</span>
        <span className="text-[10px]">{isOpen ? '▲' : '▼'}</span>
      </button>

      {isOpen && (
        <div className="mt-3 p-4 bg-panel-2 rounded-lg border border-border text-xs space-y-3">
          <div className="font-semibold text-text-primary text-sm">
            🧠 MeridianFX utiliza dos modelos complementarios
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {/* XGBoost */}
            <div className="p-3 bg-panel-3 rounded-lg border border-border/50">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-bull font-bold text-sm">▲</span>
                <span className="font-semibold text-text-primary text-sm">XGBoost</span>
                <span className="text-[10px] text-muted">(Regresión)</span>
              </div>
              <div className="text-text-secondary text-xs space-y-1">
                <div><span className="text-muted">Predice:</span> <strong className="text-text-primary">Retorno esperado</strong> (ej: +0.79%)</div>
                <div><span className="text-muted">Significa:</span> El promedio ponderado de todos los escenarios posibles</div>
                <div><span className="text-muted">Ejemplo:</span> Aunque la mayoría de los escenarios sean negativos, si los positivos son muy grandes, el promedio puede ser positivo</div>
              </div>
            </div>

            {/* Logistic */}
            <div className="p-3 bg-panel-3 rounded-lg border border-border/50">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-bear font-bold text-sm">▼</span>
                <span className="font-semibold text-text-primary text-sm">Logistic</span>
                <span className="text-[10px] text-muted">(Clasificación)</span>
              </div>
              <div className="text-text-secondary text-xs space-y-1">
                <div><span className="text-muted">Predicts:</span> <strong className="text-text-primary">Direction and probability</strong> (e.g. 65.8% Bullish)</div>
                <div><span className="text-muted">Means:</span> The probability that the price will go up or down</div>
                <div><span className="text-muted">Example:</span> 65.8% probability that the price goes up</div>
              </div>
            </div>
          </div>

          <div className="p-3 bg-primary/5 rounded-lg border border-primary/10">
            <div className="text-xs text-text-secondary">
              <span className="font-semibold text-text-primary">💡 ¿Por qué dos modelos?</span>
              <br />
              XGBoost te dice <strong className="text-text-primary">cuánto</strong> se espera que suba o baje (el promedio).
              <br />
              Logistic te dice <strong className="text-text-primary">qué tan probable</strong> es que suba o baje.
              <br />
              <span className="text-muted">Example: If XGBoost says +0.79% and Logistic says 65.8% Bullish → they are consistent.</span>
            </div>
          </div>

          <div className="text-[10px] text-muted border-t border-border pt-2">
            🔹 El <strong className="text-text-primary">retorno esperado</strong> (XGBoost) y la <strong className="text-text-primary">dirección/probabilidad</strong> (Logistic) son información complementaria.
          </div>
        </div>
      )}
    </div>
  );
}
