/**
 * PriceChartWithHover — Gráfico interactivo con hover effect (estilo SignalIQ)
 */
import { useState } from "react";

interface PricePoint {
  date: string;
  close: number;
  open: number;
  high: number;
  low: number;
}

interface PriceChartWithHoverProps {
  history: PricePoint[];
  currentPrice: number;
  pair: string;
}

export function PriceChartWithHover({ history, currentPrice, pair }: PriceChartWithHoverProps): JSX.Element {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const [period, setPeriod] = useState("30d");

  const periods = {
    "30d": 30,
    "90d": 90,
    "6m": 180,
    "1y": 365,
  };

  const limit = periods[period as keyof typeof periods] || 30;
  const filtered = history.slice(-limit);

  if (filtered.length === 0) {
    return <div className="text-center text-muted py-8">No hay datos históricos</div>;
  }

  const prices = filtered.map((p) => p.close);
  const maxPrice = Math.max(...prices, currentPrice);
  const minPrice = Math.min(...prices, currentPrice);
  const range = maxPrice - minPrice || 1;

  // Calcular tendencia
  const firstPrice = prices[0] || currentPrice;
  const lastPrice = prices[prices.length - 1] || currentPrice;
  const trend = ((lastPrice - firstPrice) / firstPrice) * 100;

  const hoveredPoint = hoveredIndex !== null ? filtered[hoveredIndex] : null;

  return (
    <div className="space-y-3">
      {/* Selector de período */}
      <div className="flex gap-1">
        {["30d", "90d", "6m", "1y"].map((p) => (
          <button
            key={p}
            onClick={() => setPeriod(p)}
            className={`px-3 py-1 text-xs rounded-md transition-colors ${
              period === p
                ? "bg-meridian text-white"
                : "bg-panel-2 text-muted hover:text-ink"
            }`}
          >
            {p}
          </button>
        ))}
      </div>

      {/* Hover tooltip */}
      {hoveredPoint && (
        <div className="bg-panel-2 rounded-lg p-3 border border-line">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-sm font-medium text-ink">{hoveredPoint.date}</span>
              <span className="text-xs text-muted ml-2">· {pair}</span>
            </div>
            <div>
              <span className="text-lg font-bold text-ink">{hoveredPoint.close.toFixed(4)}</span>
            </div>
          </div>
          <div className="flex gap-4 text-xs text-muted mt-1">
            <span>O: {hoveredPoint.open.toFixed(4)}</span>
            <span>H: {hoveredPoint.high.toFixed(4)}</span>
            <span>L: {hoveredPoint.low.toFixed(4)}</span>
          </div>
        </div>
      )}

      {/* Gráfico */}
      <div className="h-52 w-full bg-panel-2 rounded-lg p-4 relative">
        <div className="flex items-end h-40 gap-0.5">
          {filtered.map((point, i) => {
            const height = ((point.close - minPrice) / range) * 100;
            const isLast = i === filtered.length - 1;
            const isUp = i > 0 && point.close > filtered[i - 1]?.close;
            const isHovered = hoveredIndex === i;

            return (
              <div
                key={i}
                className={`flex-1 rounded-t transition-all cursor-pointer ${
                  isLast ? 'bg-meridian' :
                  isHovered ? 'bg-meridian/80' :
                  isUp ? 'bg-bull/60' : 'bg-bear/60'
                } hover:bg-meridian/50`}
                style={{ height: `${Math.max(height, 2)}%` }}
                onMouseEnter={() => setHoveredIndex(i)}
                onMouseLeave={() => setHoveredIndex(null)}
                title={`${point.date}: ${point.close.toFixed(4)}`}
              />
            );
          })}
        </div>

        {/* Fecha inicio y fin */}
        <div className="flex justify-between text-xs text-muted mt-2">
          <span>{filtered[0]?.date || ''}</span>
          <span className="font-medium text-ink">Hoy</span>
        </div>

        {/* Precio actual en el gráfico */}
        <div className="absolute right-4 top-4 text-right">
          <div className="text-xs text-muted">Actual</div>
          <div className="text-sm font-bold text-ink">{currentPrice.toFixed(4)}</div>
          <div className={`text-xs ${trend >= 0 ? 'text-bull' : 'text-bear'}`}>
            {trend >= 0 ? '▲' : '▼'} {Math.abs(trend).toFixed(2)}%
          </div>
        </div>
      </div>

      {/* Métricas rápidas */}
      <div className="grid grid-cols-4 gap-2">
        <div className="text-center p-2 bg-panel-2 rounded">
          <div className="text-xs text-muted">Máx</div>
          <div className="text-sm font-mono font-semibold">{maxPrice.toFixed(4)}</div>
        </div>
        <div className="text-center p-2 bg-panel-2 rounded">
          <div className="text-xs text-muted">Mín</div>
          <div className="text-sm font-mono font-semibold">{minPrice.toFixed(4)}</div>
        </div>
        <div className="text-center p-2 bg-panel-2 rounded">
          <div className="text-xs text-muted">Tendencia</div>
          <div className={`text-sm font-semibold ${trend >= 0 ? 'text-bull' : 'text-bear'}`}>
            {trend >= 0 ? '+' : ''}{trend.toFixed(2)}%
          </div>
        </div>
        <div className="text-center p-2 bg-panel-2 rounded">
          <div className="text-xs text-muted">Datos</div>
          <div className="text-sm font-mono font-semibold">{filtered.length} días</div>
        </div>
      </div>

      {/* Pista de interacción */}
      <div className="text-center text-xs text-muted">
        Pasa el mouse sobre el gráfico para ver el precio en cada fecha
      </div>
    </div>
  );
}
