/**
 * Drivers Page — SHAP y factores que influyen en la predicción
 */
import {
  ApiError,
  LoadingSpinner,
  Panel,
  UniverseSelector,
} from "../components/common";
import { RegimeStrip } from "../components/mockup";
import { useDrivers, useRanking, useActivePair, pairUniverseFromRanking } from "../hooks";

export function DriversPage(): JSX.Element {
  const { pair, setPair } = useActivePair();
  const ranking = useRanking();
  const drivers = useDrivers(pair);
  const universe = pairUniverseFromRanking(ranking.data);

  if (drivers.isLoading) {
    return <LoadingSpinner label={`Cargando drivers para ${pair}...`} />;
  }

  if (drivers.isError) {
    return (
      <ApiError 
        message={drivers.error?.message} 
        onRetry={() => void drivers.refetch()} 
      />
    );
  }

  const data = drivers.data;
  const features = data?.features || [];

  return (
    <section className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-2xl font-semibold text-ink">{pair} · Drivers & Explicación</h2>
        <UniverseSelector currencies={universe} selected={pair} onChange={setPair} />
      </div>

      <RegimeStrip regime="UNKNOWN" vix={16.8} riskAppetite={0.72} />

      {features.length > 0 ? (
        <div className="grid grid-cols-1 gap-6">
          {/* SHAP Values */}
          <Panel title="📊 Factores clave (SHAP)">
            <div className="space-y-4">
              {features.slice(0, 10).map((feature: any, index: number) => {
                const isPositive = feature.shap_value > 0;
                const absValue = Math.abs(feature.shap_value);
                const percentage = Math.min(absValue * 100, 100);
                
                return (
                  <div key={index} className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span className="font-medium text-ink">
                        #{index + 1} {feature.name}
                      </span>
                      <span className={`font-mono ${isPositive ? 'text-bull' : 'text-bear'}`}>
                        {isPositive ? '▲' : '▼'} {feature.shap_value.toFixed(4)}
                      </span>
                    </div>
                    <div className="w-full h-2 bg-panel-2 rounded-full overflow-hidden">
                      <div 
                        className={`h-full rounded-full ${isPositive ? 'bg-bull' : 'bg-bear'}`}
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                    <div className="text-xs text-muted">
                      Valor: {feature.value?.toFixed(4) || '—'} · Contribución: {feature.contribution || '—'}
                    </div>
                  </div>
                );
              })}
            </div>
          </Panel>

          {/* Resumen del régimen macro */}
          <Panel title="🌍 Régimen Macro">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="flex justify-between border-b border-line pb-1">
                  <span className="text-muted">Estados Unidos</span>
                  <span className="font-semibold">{data?.macro_regime?.us || '—'}</span>
                </div>
                <div className="flex justify-between border-b border-line pb-1">
                  <span className="text-muted">Japón</span>
                  <span className="font-semibold">{data?.macro_regime?.jp || '—'}</span>
                </div>
                <div className="flex justify-between border-b border-line pb-1">
                  <span className="text-muted">Riesgo</span>
                  <span className="font-semibold">{data?.macro_regime?.risk || '—'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted">Crecimiento</span>
                  <span className="font-semibold">{data?.macro_regime?.growth || '—'}</span>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between border-b border-line pb-1">
                  <span className="text-muted">Política Fed</span>
                  <span className={`font-semibold ${data?.policy_signal?.fed?.includes('Hawkish') ? 'text-bear' : 'text-bull'}`}>
                    {data?.policy_signal?.fed || '—'}
                  </span>
                </div>
                <div className="flex justify-between border-b border-line pb-1">
                  <span className="text-muted">Política BoJ</span>
                  <span className={`font-semibold ${data?.policy_signal?.boj?.includes('Dovish') ? 'text-bull' : 'text-bear'}`}>
                    {data?.policy_signal?.boj || '—'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted">Divergencia</span>
                  <span className="font-semibold text-amber">{data?.policy_signal?.divergence || '—'}</span>
                </div>
              </div>
            </div>
          </Panel>

          {/* Riesgos */}
          {data?.risks && data.risks.length > 0 && (
            <Panel title="⚠️ Riesgos">
              <div className="space-y-2">
                {data.risks.map((risk: any, index: number) => (
                  <div key={index} className="flex items-start gap-3 text-sm text-ink-soft border-b border-line pb-2 last:border-0">
                    <span className="text-amber text-base">⚠️</span>
                    <div>
                      <span>{risk.description}</span>
                      <span className="text-muted text-xs block">— {risk.probability || 'Probabilidad media'}</span>
                    </div>
                  </div>
                ))}
              </div>
            </Panel>
          )}
        </div>
      ) : (
        <div className="text-center text-muted py-8">No hay datos de drivers disponibles</div>
      )}
    </section>
  );
}
