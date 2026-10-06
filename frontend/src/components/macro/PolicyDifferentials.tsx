/**
 * PolicyDifferentials — Macro differentials and policy rates.
 *
 * ⚠️  Presentational ONLY. All values come from the backend.
 *
 * Iteración 1: cada fila tiene un tooltip explicativo con
 * "qué es", "fórmula", "fuente", "unidades" e "impacto". Los
 * textos son estáticos (no vienen del backend) porque el backend
 * aún no expone metadatos semánticos por campo.
 */
import { InfoTooltip } from "../common";

interface PolicyDifferentialsProps {
  base: string;
  quote: string;
  policyDifferential: number | null;
  growthDifferential: number | null;
  inflationDifferential: number | null;
  baseRate: number | null;
  quoteRate: number | null;
}

function formatDifferential(value: number | null): string {
  if (value == null) return "—";
  const sign = value >= 0 ? "+" : "";
  return `${sign}${value.toFixed(4)}`;
}

function formatRate(value: number | null): string {
  if (value == null) return "—";
  return `${value.toFixed(3)}%`;
}

export function PolicyDifferentials({
  base,
  quote,
  policyDifferential,
  growthDifferential,
  inflationDifferential,
  baseRate,
  quoteRate,
}: PolicyDifferentialsProps): JSX.Element {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-y-3 gap-x-6 text-sm">
      <div className="flex justify-between border-b border-line pb-2">
        <span className="text-muted inline-flex items-center">
          Policy differential
          <InfoTooltip title="Policy differential">
            <span className="block mb-1">
              <strong className="text-ink">Qué es:</strong> diferencia entre la
              tasa de política monetaria del {base} y la del {quote}.
            </span>
            <span className="block mb-1">
              <strong className="text-ink">Fórmula:</strong> {base} rate − {quote} rate
            </span>
            <span className="block mb-1">
              <strong className="text-ink">Fuente:</strong> FRED (USA) · banco
              central de {quote}.
            </span>
            <span className="block mb-1">
              <strong className="text-ink">Unidades:</strong> puntos porcentuales (pp).
            </span>
            <span className="block">
              <strong className="text-ink">Impacto:</strong> &gt; 0 → carry trade
              favorable al {base}; &lt; 0 → favorable al {quote}.
            </span>
          </InfoTooltip>
        </span>
        <span className="font-mono font-semibold text-ink">
          {formatDifferential(policyDifferential)}
        </span>
      </div>

      <div className="flex justify-between border-b border-line pb-2">
        <span className="text-muted inline-flex items-center">
          Growth differential
          <InfoTooltip title="Growth differential">
            <span className="block mb-1">
              <strong className="text-ink">Qué es:</strong> diferencia en el
              ritmo de crecimiento económico entre EE.UU. y el país del {quote}.
            </span>
            <span className="block mb-1">
              <strong className="text-ink">Fórmula:</strong> PMI USA − PMI {quote}
            </span>
            <span className="block mb-1">
              <strong className="text-ink">Fuente:</strong> FRED MANPMI (USA) ·
              índice PMI nacional de {quote}.
            </span>
            <span className="block mb-1">
              <strong className="text-ink">Unidades:</strong> puntos de índice
              (pt). 50 = neutral, &gt; 50 expansión, &lt; 50 contracción.
            </span>
            <span className="block">
              <strong className="text-ink">Impacto:</strong> &gt; 0 → USD más
              fuerte; &lt; 0 → {quote} más fuerte.
            </span>
          </InfoTooltip>
        </span>
        <span className="font-mono font-semibold text-ink">
          {formatDifferential(growthDifferential)}
        </span>
      </div>

      <div className="flex justify-between border-b border-line pb-2">
        <span className="text-muted inline-flex items-center">
          Inflation differential
          <InfoTooltip title="Inflation differential">
            <span className="block mb-1">
              <strong className="text-ink">Qué es:</strong> diferencia en la
              inflación interanual entre EE.UU. y el país del {quote}.
            </span>
            <span className="block mb-1">
              <strong className="text-ink">Fórmula:</strong> CPI USA YoY − CPI {quote} YoY
            </span>
            <span className="block mb-1">
              <strong className="text-ink">Fuente:</strong> FRED CPIAUCSL (USA) ·
              instituto nacional de estadística de {quote}.
            </span>
            <span className="block mb-1">
              <strong className="text-ink">Unidades:</strong> puntos porcentuales (pp).
            </span>
            <span className="block">
              <strong className="text-ink">Impacto:</strong> según paridad de poder
              adquisitivo, &gt; 0 → presión depreciatoria sobre el {base}; &lt; 0 →
              presión apreciatoria.
            </span>
          </InfoTooltip>
        </span>
        <span className="font-mono font-semibold text-ink">
          {formatDifferential(inflationDifferential)}
        </span>
      </div>

      <div className="flex justify-between border-b border-line pb-2">
        <span className="text-muted inline-flex items-center">
          {base} rate
          <InfoTooltip title={`${base} policy rate`}>
            <span className="block mb-1">
              <strong className="text-ink">Qué es:</strong> tasa de política
              monetaria del banco central del {base}.
            </span>
            <span className="block mb-1">
              <strong className="text-ink">Fuente:</strong> FRED DFF · banco
              central del {base}.
            </span>
            <span className="block mb-1">
              <strong className="text-ink">Unidades:</strong> porcentaje anual (%).
            </span>
            <span className="block">
              <strong className="text-ink">Impacto:</strong> tasa alta → moneda
              atractiva para carry trade.
            </span>
          </InfoTooltip>
        </span>
        <span className="font-mono font-semibold text-ink">
          {formatRate(baseRate)}
        </span>
      </div>

      <div className="flex justify-between border-b border-line pb-2">
        <span className="text-muted inline-flex items-center">
          {quote} rate
          <InfoTooltip title={`${quote} policy rate`}>
            <span className="block mb-1">
              <strong className="text-ink">Qué es:</strong> tasa de política
              monetaria del banco central del {quote}.
            </span>
            <span className="block mb-1">
              <strong className="text-ink">Fuente:</strong> banco central del {quote}.
            </span>
            <span className="block mb-1">
              <strong className="text-ink">Unidades:</strong> porcentaje anual (%).
            </span>
            <span className="block">
              <strong className="text-ink">Nota:</strong> cuando aparece "—", el
              banco central del {quote} no publica la tasa en una fuente accesible
              al sistema. Puede ser un régimen administrado (CNY, ARS, BOB).
            </span>
          </InfoTooltip>
        </span>
        <span className="font-mono font-semibold text-ink">
          {formatRate(quoteRate)}
        </span>
      </div>
    </div>
  );
}
