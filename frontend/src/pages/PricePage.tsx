import { safeToFixed } from "../utils/safeFormat";
/**
 * Price Page — Cotización actual, histórico y predicción
 */
import { useState } from "react";
import { useActivePair } from "../hooks/useActivePair";
import { UniverseSelector } from "../components/common/UniverseSelector";
import { useRanking, pairUniverseFromRanking } from "../hooks";
import { usePrice } from "../hooks/usePrice";
import { LoadingSpinner } from "../components/common/LoadingSpinner";
import { ApiError } from "../components/common/ApiError";
import { Panel } from "../components/common/Panel";

export function PricePage(): JSX.Element {
  const { pair, setPair } = useActivePair();
  const ranking = useRanking();
  const universe = pairUniverseFromRanking(ranking.data);
  const [period, setPeriod] = useState("1y");
  const { data, isLoading, error, refetch } = usePrice(pair, period);

  if (isLoading) return <LoadingSpinner label={`Cargando datos para ${pair}...`} />;
  if (error) return <ApiError message={error?.message} onRetry={() => refetch()} />;
  if (!data) return <div>No hay datos disponibles</div>;

  const {
    current_price,
    change_percent,
    change_abs,
    direction,
    probability,
    info,
    history,
    source,
    freshness,
    last_date,
    base_name,
    quote_name,
  } = data;

  // Calcular máximo y mínimo del histórico
  const prices = history?.map((p: any) => p.close) || [];
  const maxPrice = prices.length > 0 ? Math.max(...prices) : current_price;
  const minPrice = prices.length > 0 ? Math.min(...prices) : current_price;
  const volatility = maxPrice > 0 && minPrice > 0 ? ((maxPrice - minPrice) / minPrice) * 100 : 0;

  // Últimos 30 días para el gráfico
  const last30 = history?.slice(-30) || [];

  return (
    <section className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-2xl font-semibold text-ink">{pair} · Precio y Predicción</h2>
        <div className="flex items-center gap-3">
          <PeriodSelector period={period} onChange={setPeriod} />
          <UniverseSelector currencies={universe} selected={pair} onChange={setPair} />
        </div>
      </div>

      {/* Precio actual */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4 bg-panel rounded-lg p-6 border border-line">
        <div>
          <div className="text-sm text-muted">Precio Actual</div>
          <div className="text-3xl font-bold text-ink">{safeToFixed(current_price, 4)}</div>
          <div className="text-sm text-muted">{info}</div>
        </div>
        <div>
          <div className="text-sm text-muted">Cambio (24h)</div>
          <div className={`text-2xl font-bold ${change_percent >= 0 ? 'text-bull' : 'text-bear'}`}>
            {change_percent >= 0 ? '+' : ''}{safeToFixed(change_percent, 2)}%
          </div>
          <div className="text-sm text-muted">{change_abs >= 0 ? '+' : ''}{safeToFixed(change_abs, 4)}</div>
        </div>
        <div>
          <div className="text-sm text-muted">Predicción XGBoost</div>
          <div className={`text-2xl font-bold ${direction === 'UP' ? 'text-bull' : direction === 'DOWN' ? 'text-bear' : 'text-muted'}`}>
            {direction === 'UP' ? '▲ Alcista' : direction === 'DOWN' ? '▼ Bajista' : '—'}
          </div>
          <div className="text-sm text-muted">Confianza: {(probability * 100).toFixed(1)}%</div>
        </div>
        <div>
          <div className="text-sm text-muted">Fuente</div>
          <div className="text-lg font-semibold text-ink">{source || 'yahoo'}</div>
          <div className="text-sm text-muted">{freshness || 'UNKNOWN'}</div>
        </div>
        <div>
          <div className="text-sm text-muted">Última actualización</div>
          <div className="text-lg font-semibold text-ink">{last_date || '—'}</div>
          <div className="text-sm text-muted">{new Date(data.timestamp).toLocaleTimeString()}</div>
        </div>
      </div>

      {/* Gráfico histórico */}
      {last30.length > 0 && (
        <Panel title={`📈 Histórico (últimos ${last30.length} días)`}>
          <div className="h-64 w-full">
            <div className="flex items-end h-48 gap-0.5">
              {last30.map((point: any, i: number) => {
                const range = maxPrice - minPrice || 1;
                const height = ((point.close - minPrice) / range) * 100;
                const isLast = i === last30.length - 1;
                return (
                  <div
                    key={i}
                    className={`flex-1 ${isLast ? 'bg-meridian' : 'bg-meridian/40'} rounded-t transition-all hover:bg-meridian/80`}
                    style={{ height: `${Math.max(height, 2)}%` }}
                    title={`${point.date}: ${safeToFixed(point.close, 4)}`}
                  />
                );
              })}
            </div>
          </div>
          <div className="flex justify-between text-xs text-muted mt-2">
            <span>{last30[0]?.date || ''}</span>
            <span>Hoy</span>
          </div>
        </Panel>
      )}

      {/* Estadísticas */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 bg-panel rounded-lg p-6 border border-line">
        <div className="text-center">
          <div className="text-xs text-muted">Máximo (30d)</div>
          <div className="text-lg font-mono font-semibold text-ink">{safeToFixed(maxPrice, 4)}</div>
        </div>
        <div className="text-center">
          <div className="text-xs text-muted">Mínimo (30d)</div>
          <div className="text-lg font-mono font-semibold text-ink">{safeToFixed(minPrice, 4)}</div>
        </div>
        <div className="text-center">
          <div className="text-xs text-muted">Volatilidad (30d)</div>
          <div className="text-lg font-mono font-semibold text-ink">{safeToFixed(volatility, 2)}%</div>
        </div>
        <div className="text-center">
          <div className="text-xs text-muted">Rango</div>
          <div className="text-lg font-mono font-semibold text-ink">{safeToFixed(maxPrice - minPrice, 4)}</div>
        </div>
      </div>

      {/* Interpretación */}
      <Panel title="🧠 Interpretación">
        <div className="space-y-2">
          <p className="text-sm text-ink-soft">
            {direction === 'UP'
              ? `El modelo XGBoost predice que ${base_name} se fortalecerá frente a ${quote_name} con una confianza del ${(probability * 100).toFixed(1)}%.`
              : direction === 'DOWN'
              ? `El modelo XGBoost predice que ${base_name} se debilitará frente a ${quote_name} con una confianza del ${(probability * 100).toFixed(1)}%.`
              : `No hay suficiente información para una predicción confiable.`}
          </p>
          <p className="text-xs text-muted">
            Precio actual: 1 {base_name} = {safeToFixed(current_price, 4)} {quote_name}
          </p>
          <p className="text-xs text-muted">
            Datos históricos: {history?.length || 0} días · Fuente: {source || 'yahoo'}
          </p>
        </div>
      </Panel>
    </section>
  );
}

function PeriodSelector({ period, onChange }: { period: string; onChange: (p: string) => void }) {
  const periods = ["1m", "3m", "6m", "1y"];
  return (
    <div className="flex items-center gap-1 bg-panel-2 rounded-lg p-1">
      {periods.map((p) => (
        <button
          key={p}
          type="button"
          onClick={() => onChange(p)}
          className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
            p === period
              ? "bg-meridian text-white"
              : "text-muted hover:text-ink hover:bg-panel"
          }`}
        >
          {p}
        </button>
      ))}
    </div>
  );
}
