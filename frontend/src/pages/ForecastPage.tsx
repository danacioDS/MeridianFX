/**
 * Forecast Dashboard — Con datos reales y Why Now? por LLM
 */
import {
  ApiError,
  LoadingSpinner,
  Panel,
  UniverseSelector,
} from "../components/common";
import { RegimeStrip } from "../components/mockup";
import { MacroPanel } from "../components/macro";
import { useForecast, useRanking, useActivePair, pairUniverseFromRanking, useInterpretation, useMacroContext } from "../hooks";

export function ForecastPage(): JSX.Element {
  const { pair, setPair } = useActivePair();
  const ranking = useRanking();
  const forecast = useForecast(pair);
  const interpretation = useInterpretation(pair);
  const macro = useMacroContext();
  const universe = pairUniverseFromRanking(ranking.data);

  if (forecast.isLoading) {
    return <LoadingSpinner label={`Cargando forecast para ${pair}...`} />;
  }

  if (forecast.isError) {
    return (
      <ApiError 
        message={forecast.error?.message} 
        onRetry={() => void forecast.refetch()} 
      />
    );
  }

  const data = forecast.data;
  const prediction = data?.prediction;
  const decision = data?.decision;
  const interpretationData = interpretation.data;
  const macroData = macro.data;

  return (
    <section className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-2xl font-semibold text-ink">{pair} · Forecast Dashboard</h2>
        <UniverseSelector currencies={universe} selected={pair} onChange={setPair} />
      </div>

      <RegimeStrip regime="UNKNOWN" vix={16.8} riskAppetite={0.72} />

      {/* Macro Panel - primera fila */}
      {macroData?.macro && (
        <div className="w-full">
          <MacroPanel macro={macroData.macro} isLoading={macro.isLoading} />
        </div>
      )}

      {prediction ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Panel - Predicción */}
          <Panel title="📊 Predicción">
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <span className={`text-4xl font-bold ${prediction.direction === 'UP' ? 'text-bull' : 'text-bear'}`}>
                  {prediction.direction === 'UP' ? '▲' : '▼'}
                </span>
                <div>
                  <div className="text-2xl font-semibold">
                    {prediction.direction === 'UP' ? 'Alcista' : 'Bajista'}
                  </div>
                  <div className="text-muted text-sm">Dirección predicha</div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 border-t border-line pt-4">
                <div>
                  <div className="text-muted text-sm">Probabilidad</div>
                  <div className="text-2xl font-mono font-semibold text-meridian">
                    {(prediction.probability * 100).toFixed(1)}%
                  </div>
                </div>
                <div>
                  <div className="text-muted text-sm">Retorno esperado</div>
                  <div className={`text-2xl font-mono font-semibold ${(prediction.expected_return || 0) >= 0 ? 'text-bull' : 'text-bear'}`}>
                    {(prediction.expected_return || 0) >= 0 ? '+' : ''}{(prediction.expected_return || 0).toFixed(4)}%
                  </div>
                </div>
              </div>
            </div>
          </Panel>

          {/* Panel - Decisión */}
          <Panel title="⚡ Decisión">
            <div className="space-y-3">
              <div className="flex justify-between border-b border-line pb-2">
                <span className="text-muted">Accionable</span>
                <span className={`font-semibold ${decision?.actionable ? 'text-bull' : 'text-muted'}`}>
                  {decision?.actionable ? '✅ Sí' : '❌ No'}
                </span>
              </div>
              <div className="flex justify-between border-b border-line pb-2">
                <span className="text-muted">Confianza</span>
                <span className="font-mono font-semibold">
                  {(decision?.confidence || 0) > 0.7 ? 'ALTA' : (decision?.confidence || 0) > 0.4 ? 'MEDIA' : 'BAJA'}
                </span>
              </div>
              <div className="flex justify-between border-b border-line pb-2">
                <span className="text-muted">Edge Ratio</span>
                <span className="font-mono font-semibold">{decision?.edge_ratio?.toFixed(3) || '—'}x</span>
              </div>
              <div className="flex justify-between border-b border-line pb-2">
                <span className="text-muted">Retorno Neto</span>
                <span className={`font-mono font-semibold ${(decision?.net_return || 0) >= 0 ? 'text-bull' : 'text-bear'}`}>
                  {(decision?.net_return || 0) >= 0 ? '+' : ''}{(decision?.net_return || 0).toFixed(4)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted">Tamaño de posición</span>
                <span className="font-mono font-semibold">{decision?.position_size || 0}</span>
              </div>
            </div>
          </Panel>

          {/* Why Now? - con bullets económicos */}
          {interpretationData?.interpretation && (
            <div className="lg:col-span-2">
              <Panel title="🧠 Why Now?">
                <ul className="space-y-2.5 text-ink-soft text-base">
                  {interpretationData.interpretation.map((bullet: string, index: number) => (
                    <li key={index} className="flex items-start gap-2.5">
                      <span className="text-meridian font-bold mt-0.5 text-lg">•</span>
                      <span className="leading-relaxed">{bullet}</span>
                    </li>
                  ))}
                </ul>
                <div className="text-xs text-muted border-t border-line pt-2.5 mt-2.5 flex justify-between">
                  <span>AI interpretation · Based on MeridianFX economic signals</span>
                  <span className="font-mono">{interpretationData.timestamp ? new Date(interpretationData.timestamp).toLocaleTimeString() : '—'}</span>
                </div>
              </Panel>
            </div>
          )}

          {/* Información del Modelo */}
          <div className="lg:col-span-2">
            <Panel title="ℹ️ Información del Modelo">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <div className="text-muted text-sm">Modelo</div>
                  <div className="font-semibold">{data?.lineage?.model?.type || '—'}</div>
                </div>
                <div>
                  <div className="text-muted text-sm">Versión</div>
                  <div className="font-mono font-semibold">{data?.lineage?.model?.version || '—'}</div>
                </div>
                <div>
                  <div className="text-muted text-sm">Última actualización</div>
                  <div className="font-mono text-sm">
                    {data?.timestamp ? new Date(data.timestamp).toLocaleTimeString() : '—'}
                  </div>
                </div>
              </div>
            </Panel>
          </div>
        </div>
      ) : (
        <div className="text-center text-muted py-8">No hay datos de forecast disponibles</div>
      )}
    </section>
  );
}
