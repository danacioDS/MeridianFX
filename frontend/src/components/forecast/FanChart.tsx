/**
 * Fan Chart — Visualización probabilística del forecast
 * 
 * Muestra P10, P25, P50, P75, P90 con área sombreada
 */
import {
  ResponsiveContainer,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Area,
  ComposedChart,
} from 'recharts';

interface FanChartData {
  date: string;
  p10: number;
  p25: number;
  p50: number;
  p75: number;
  p90: number;
  actual?: number;
}

interface FanChartProps {
  data: FanChartData[];
  currentPrice: number;
  currentDate: string;
  title?: string;
}

export function FanChart({ data, currentPrice, currentDate, title = 'Probabilistic Forecast' }: FanChartProps): JSX.Element {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-muted text-sm">
        No hay datos suficientes para el fan chart
      </div>
    );
  }

  // Preparar datos para Recharts
  const chartData = [
    { date: currentDate, p10: currentPrice, p25: currentPrice, p50: currentPrice, p75: currentPrice, p90: currentPrice, actual: currentPrice },
    ...data
  ];

  return (
    <div className="w-full">
      <h3 className="text-sm font-semibold text-text-primary mb-3">{title}</h3>
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 10, right: 30, left: 10, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2A2A3A" />
            <XAxis 
              dataKey="date" 
              stroke="#8A8A9A" 
              tick={{ fontSize: 11 }}
              tickFormatter={(value) => value.split('-').slice(1).join('/')}
            />
            <YAxis 
              stroke="#8A8A9A" 
              tick={{ fontSize: 11 }}
              domain={['auto', 'auto']}
              tickFormatter={(value) => value.toFixed(2)}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#14141D',
                borderColor: '#2A2A3A',
                borderRadius: '8px',
                color: '#FFFFFF',
              }}
              labelStyle={{ color: '#8A8A9A' }}
              formatter={(value: number) => value.toFixed(4)}
            />
            
            {/* Áreas del fan chart */}
            <Area
              type="monotone"
              dataKey="p90"
              stroke="none"
              fill="#00D4AA"
              fillOpacity={0.05}
            />
            <Area
              type="monotone"
              dataKey="p10"
              stroke="none"
              fill="#00D4AA"
              fillOpacity={0.05}
            />
            <Area
              type="monotone"
              dataKey="p75"
              stroke="none"
              fill="#00D4AA"
              fillOpacity={0.10}
            />
            <Area
              type="monotone"
              dataKey="p25"
              stroke="none"
              fill="#00D4AA"
              fillOpacity={0.10}
            />
            
            {/* Líneas P10-P90 */}
            <Line type="monotone" dataKey="p10" stroke="#00D4AA" strokeWidth={1} strokeOpacity={0.3} dot={false} />
            <Line type="monotone" dataKey="p25" stroke="#00D4AA" strokeWidth={1.5} strokeOpacity={0.5} dot={false} />
            <Line type="monotone" dataKey="p50" stroke="#FFFFFF" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="p75" stroke="#00D4AA" strokeWidth={1.5} strokeOpacity={0.5} dot={false} />
            <Line type="monotone" dataKey="p90" stroke="#00D4AA" strokeWidth={1} strokeOpacity={0.3} dot={false} />
            
            {/* Línea actual */}
            {data[0]?.actual && (
              <Line type="monotone" dataKey="actual" stroke="#F5A623" strokeWidth={2} strokeDasharray="5 5" dot={false} />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      
      {/* Leyenda */}
      <div className="flex flex-wrap items-center gap-4 mt-3 text-xs text-muted">
        <div className="flex items-center gap-2">
          <span className="w-8 h-0.5 bg-white" />
          <span>P50 (Mediana)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-8 h-0.5 bg-primary/50" />
          <span>P25 - P75 (50% CI)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-8 h-0.5 bg-primary/30" />
          <span>P10 - P90 (80% CI)</span>
        </div>
        {data[0]?.actual && (
          <div className="flex items-center gap-2">
            <span className="w-8 h-0.5 border-t-2 border-dashed border-warning" />
            <span>Actual</span>
          </div>
        )}
      </div>
    </div>
  );
}
