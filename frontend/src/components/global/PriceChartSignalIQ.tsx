/**
 * PriceChartSignalIQ — Chart with area + projection line
 */
import {
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { useState } from "react";

interface PricePoint {
  date: string;
  close: number;
  open: number;
  high: number;
  low: number;
}

interface PriceChartSignalIQProps {
  history: PricePoint[];
  currentPrice: number;
  pair: string;
  isMobile?: boolean;
  /**
   * Optional projected series (rolling ARIMA(1,0,1) under clean float).
   * When provided, an additional yellow dashed line is drawn on the
   * chart. Each entry is [YYYY-MM-DD, price].
   */
  projectedSeries?: [string, number][];
}

export function PriceChartSignalIQ({
  history,
  currentPrice,
  isMobile = false,
  projectedSeries,
}: PriceChartSignalIQProps): JSX.Element {
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
    return <div className="text-center text-muted py-8">No historical data</div>;
  }

  // Build a lookup of projected values by original date (YYYY-MM-DD).
  const projectedByDate = new Map<string, number>();
  if (projectedSeries) {
    for (const [d, v] of projectedSeries) {
      projectedByDate.set(d, v);
    }
  }

  const chartData = filtered.map((p) => ({
    date: p.date.slice(5),
    close: p.close,
    open: p.open,
    high: p.high,
    low: p.low,
    // Look up by original full date (before slice) to avoid collisions.
    projected: projectedByDate.get(p.date),
  }));

  const hasProjection = projectedByDate.size > 0;

  const prices = filtered.map((p) => p.close);
  const minPrice = Math.min(...prices, currentPrice);
  const maxPrice = Math.max(...prices, currentPrice);
  const padding = (maxPrice - minPrice) * 0.08 || 1;

  // Colores estilo SignalIQ
  const accentColor = "#00d4aa";
  const textColor = "#8a8a9a";
  const cardBg = "#1a1a2e";

  return (
    <div className="space-y-4">
      {/* Period selector */}
      <div className="flex gap-1">
        {["30d", "90d", "6m", "1y"].map((p) => (
          <button
            key={p}
            onClick={() => setPeriod(p)}
            className={`px-3 py-1 text-xs rounded-md transition-colors ${
              period === p
                ? "bg-[#00d4aa] text-white"
                : "bg-[#2a2a3e] text-[#8a8a9a] hover:text-white"
            }`}
          >
            {p}
          </button>
        ))}
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-4 text-xs text-[#8a8a9a]">
        <div className="flex items-center gap-2">
          <span
            className="inline-block w-6 h-0.5 rounded"
            style={{ backgroundColor: "#00d4aa" }}
          />
          <span>Observed price</span>
        </div>
        {hasProjection && (
          <div className="flex items-center gap-2">
            <span
              className="inline-block w-6 h-0.5 rounded"
              style={{
                backgroundImage:
                  "repeating-linear-gradient(to right, #ffd84a 0 4px, transparent 4px 8px)",
              }}
            />
            <span>Clean-float projection (rolling ARIMA 1,0,1)</span>
          </div>
        )}
      </div>

      {/* Chart */}
      <div className="bg-[#1a1a2e] rounded-lg p-4">
        <ResponsiveContainer width="100%" height={isMobile ? 150 : 220}>
          <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 10 }}>
            <defs>
              <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={accentColor} stopOpacity={0.3} />
                <stop offset="95%" stopColor={accentColor} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
            <XAxis
              dataKey="date"
              tick={{ fill: textColor, fontSize: isMobile ? 7 : 9 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              domain={[minPrice - padding, maxPrice + padding]}
              tick={{ fill: textColor, fontSize: isMobile ? 7 : 9 }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(value) => value.toFixed(2)}
              width={isMobile ? 35 : 50}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: cardBg,
                border: `1px solid #333`,
                borderRadius: 8,
                padding: "8px 12px",
              }}
              labelStyle={{ color: "#fff", fontSize: "11px" }}
              formatter={(value: any, name: string) => [
                value.toFixed(4),
                name === "projected" ? "Clean-float projection" : "Observed price",
              ]}
            />
            <ReferenceLine
              y={currentPrice}
              stroke={accentColor}
              strokeDasharray="3 3"
              label={{
                value: `Current ${currentPrice.toFixed(4)}`,
                fill: accentColor,
                fontSize: 9,
                position: "right",
              }}
            />
            <Area
              type="monotone"
              dataKey="close"
              stroke={accentColor}
              strokeWidth={2}
              fill="url(#priceGradient)"
            />
            {hasProjection && (
              <Line
                type="monotone"
                dataKey="projected"
                stroke="#ffd84a"
                strokeWidth={1.5}
                strokeDasharray="4 4"
                dot={false}
                activeDot={false}
                connectNulls={false}
                name="Clean-float projection"
              />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Quick metrics */}
      <div className="grid grid-cols-4 gap-2">
        <div className="text-center p-2 bg-[#2a2a3e] rounded">
          <div className="text-xs text-[#8a8a9a]">Max</div>
          <div className="text-sm font-mono font-semibold text-white">{maxPrice.toFixed(4)}</div>
        </div>
        <div className="text-center p-2 bg-[#2a2a3e] rounded">
          <div className="text-xs text-[#8a8a9a]">Min</div>
          <div className="text-sm font-mono font-semibold text-white">{minPrice.toFixed(4)}</div>
        </div>
        <div className="text-center p-2 bg-[#2a2a3e] rounded">
          <div className="text-xs text-[#8a8a9a]">Range</div>
          <div className="text-sm font-mono font-semibold text-white">{(maxPrice - minPrice).toFixed(4)}</div>
        </div>
        <div className="text-center p-2 bg-[#2a2a3e] rounded">
          <div className="text-xs text-[#8a8a9a]">Data</div>
          <div className="text-sm font-mono font-semibold text-white">{filtered.length} days</div>
        </div>
      </div>
    </div>
  );
}
