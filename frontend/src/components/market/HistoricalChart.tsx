import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useState } from "react";

export interface HistoricalPoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface HistoricalChartProps {
  history: HistoricalPoint[];
  pair: string;
  currentPrice: number;
}

const PERIODS = {
  "30d": 30,
  "90d": 90,
  "6m": 180,
  "1y": 365,
} as const;

export function HistoricalChart({
  history,
  pair,
  currentPrice,
}: HistoricalChartProps): JSX.Element {
  const [period, setPeriod] =
    useState<keyof typeof PERIODS>("30d");

  const filtered = history.slice(-PERIODS[period]);

  if (filtered.length === 0) {
    return (
      <div className="text-center text-muted py-8">
        No hay datos históricos disponibles
      </div>
    );
  }

  const chartData = filtered.map((point) => ({
    ...point,
    label: point.date.slice(5),
  }));

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <div className="text-sm font-medium text-ink">
            Historical Price
          </div>
          <div className="text-xs text-muted">{pair}</div>
        </div>

        <div className="flex gap-1">
          {(Object.keys(PERIODS) as Array<keyof typeof PERIODS>).map(
            (value) => (
              <button
                key={value}
                type="button"
                onClick={() => setPeriod(value)}
                className={`px-3 py-1 text-xs rounded-md transition-colors ${
                  period === value
                    ? "bg-meridian text-white"
                    : "bg-panel-2 text-muted hover:text-ink"
                }`}
              >
                {value}
              </button>
            )
          )}
        </div>
      </div>

      <div className="h-64 w-full bg-panel-2 rounded-lg p-3">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={chartData}
            margin={{
              top: 10,
              right: 10,
              left: 0,
              bottom: 5,
            }}
          >
            <defs>
              <linearGradient
                id="marketPriceGradient"
                x1="0"
                y1="0"
                x2="0"
                y2="1"
              >
                <stop
                  offset="5%"
                  stopColor="var(--meridian)"
                  stopOpacity={0.25}
                />
                <stop
                  offset="95%"
                  stopColor="var(--meridian)"
                  stopOpacity={0}
                />
              </linearGradient>
            </defs>

            <CartesianGrid
              strokeDasharray="3 3"
              stroke="var(--line)"
              vertical={false}
            />

            <XAxis
              dataKey="label"
              tick={{
                fontSize: 10,
                fill: "var(--muted)",
              }}
              tickLine={false}
              axisLine={false}
              minTickGap={24}
            />

            <YAxis
              domain={["auto", "auto"]}
              tick={{
                fontSize: 10,
                fill: "var(--muted)",
              }}
              tickLine={false}
              axisLine={false}
              width={55}
              tickFormatter={(value) =>
                Number(value).toFixed(4)
              }
            />

            <Tooltip
              content={({ active, payload }) => {
                if (!active || !payload?.length) return null;

                const point = payload[0]?.payload as HistoricalPoint & {
                  label: string;
                };

                return (
                  <div className="bg-panel border border-line rounded-lg p-3 shadow-lg">
                    <div className="text-xs text-muted mb-1">
                      {point.date}
                    </div>

                    <div className="text-sm font-semibold text-ink">
                      Close: {point.close.toFixed(4)}
                    </div>

                    <div className="grid grid-cols-2 gap-x-3 text-xs text-muted mt-1">
                      <span>
                        O: {point.open.toFixed(4)}
                      </span>
                      <span>
                        H: {point.high.toFixed(4)}
                      </span>
                      <span>
                        L: {point.low.toFixed(4)}
                      </span>
                      <span>
                        V: {point.volume}
                      </span>
                    </div>
                  </div>
                );
              }}
            />

            <Area
              type="monotone"
              dataKey="close"
              stroke="var(--meridian)"
              fill="url(#marketPriceGradient)"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="text-xs text-muted">
        Current price: {currentPrice.toFixed(4)}
      </div>
    </div>
  );
}
