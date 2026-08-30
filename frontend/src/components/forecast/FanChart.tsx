/**
 * Fan Chart — Estilo institucional para Meridian FX
 * 
 * Diseño profesional con:
 * - Degradado de bandas probabilísticas
 * - Línea P50 prominente
 * - Tooltip completo
 * - Separador NOW
 * - Paleta azul sobria
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
  ReferenceLine,
} from 'recharts';
import { useMemo } from 'react';

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
  isMobile?: boolean;
}

// Paleta institucional
const COLORS = {
  median: '#60A5FA',
  bandOuter: 'rgba(37, 99, 235, 0.08)',
  bandOuterStroke: 'rgba(37, 99, 235, 0.25)',
  bandMid: 'rgba(59, 130, 246, 0.15)',
  bandMidStroke: 'rgba(59, 130, 246, 0.35)',
  grid: 'rgba(255,255,255,0.04)',
  text: '#FFFFFF',
  muted: '#8A8A9A',
  panel: '#14141D',
  border: '#2A2A3A',
};

const formatDate = (value: string) => {
  if (!value) return '';
  const parts = value.split('-');
  if (parts.length !== 3) return value;
  return `${parts[2]}/${parts[1]}`;
};

const formatPrice = (value: number) => {
  if (!Number.isFinite(value)) return '—';
  return value.toFixed(4);
};

const FanTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload || payload.length === 0) return null;

  const values = new Map(payload.map((item: any) => [item.dataKey, item.value]));

  return (
    <div style={{
      background: COLORS.panel,
      border: `1px solid ${COLORS.border}`,
      borderRadius: 12,
      padding: '16px 20px',
      minWidth: 220,
      boxShadow: '0 20px 60px rgba(0,0,0,0.6)',
    }}>
      <div style={{
        color: COLORS.muted,
        fontSize: 11,
        marginBottom: 10,
        letterSpacing: '0.04em',
        textTransform: 'uppercase',
      }}>
        {formatDate(label || '')}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 6, fontSize: 12 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 24 }}>
          <span style={{ color: COLORS.muted }}>P10 (80% CI)</span>
          <span style={{ color: '#93C5FD', fontFamily: 'monospace' }}>
            {formatPrice(Number(values.get('p10')))}
          </span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 24 }}>
          <span style={{ color: COLORS.muted }}>P25 (50% CI)</span>
          <span style={{ color: '#60A5FA', fontFamily: 'monospace' }}>
            {formatPrice(Number(values.get('p25')))}
          </span>
        </div>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          gap: 24,
          padding: '8px 0',
          borderTop: `1px solid ${COLORS.border}`,
          borderBottom: `1px solid ${COLORS.border}`,
        }}>
          <span style={{ color: COLORS.text, fontWeight: 600 }}>P50 (Mediana)</span>
          <span style={{ color: COLORS.text, fontWeight: 600, fontFamily: 'monospace' }}>
            {formatPrice(Number(values.get('p50')))}
          </span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 24 }}>
          <span style={{ color: COLORS.muted }}>P75 (50% CI)</span>
          <span style={{ color: '#60A5FA', fontFamily: 'monospace' }}>
            {formatPrice(Number(values.get('p75')))}
          </span>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 24 }}>
          <span style={{ color: COLORS.muted }}>P90 (80% CI)</span>
          <span style={{ color: '#93C5FD', fontFamily: 'monospace' }}>
            {formatPrice(Number(values.get('p90')))}
          </span>
        </div>
      </div>

      <div style={{
        marginTop: 10,
        paddingTop: 10,
        borderTop: `1px solid ${COLORS.border}`,
        fontSize: 10,
        color: COLORS.muted,
        display: 'flex',
        flexDirection: 'column',
        gap: 4,
      }}>
        <div>
          <span>50% CI: </span>
          <span style={{ color: '#60A5FA', fontFamily: 'monospace' }}>
            {formatPrice(Number(values.get('p25')))} — {formatPrice(Number(values.get('p75')))}
          </span>
        </div>
        <div>
          <span>80% CI: </span>
          <span style={{ color: '#93C5FD', fontFamily: 'monospace' }}>
            {formatPrice(Number(values.get('p10')))} — {formatPrice(Number(values.get('p90')))}
          </span>
        </div>
      </div>
    </div>
  );
};

export function FanChart({
  data,
  currentPrice,
  currentDate,
  title = 'Probabilistic Forecast',
  isMobile = false,
}: FanChartProps): JSX.Element {
  const allPrices = useMemo(() => {
    const prices = data.flatMap(d => [d.p10, d.p25, d.p50, d.p75, d.p90, currentPrice]);
    const valid = prices.filter(p => Number.isFinite(p) && p > 0);
    if (valid.length === 0) return { min: currentPrice * 0.9, max: currentPrice * 1.1 };
    const min = Math.min(...valid);
    const max = Math.max(...valid);
    const padding = (max - min) * 0.12;
    return { min: Math.max(0, min - padding), max: max + padding };
  }, [data, currentPrice]);

  if (!data || data.length === 0) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: 300,
        color: COLORS.muted,
        fontSize: 13,
        background: 'rgba(255,255,255,0.015)',
        borderRadius: 12,
      }}>
        No hay datos suficientes para el fan chart
      </div>
    );
  }

  const chartData = [
    {
      date: currentDate,
      p10: currentPrice,
      p25: currentPrice,
      p50: currentPrice,
      p75: currentPrice,
      p90: currentPrice,
    },
    ...data.map((point) => ({ ...point })),
  ];

  return (
    <div style={{ width: '100%' }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'baseline',
        gap: 12,
        flexWrap: 'wrap',
        marginBottom: 12,
      }}>
        <div>
          <h3 style={{
            fontSize: 15,
            fontWeight: 600,
            color: COLORS.text,
            margin: 0,
          }}>
            {title}
          </h3>
          <div style={{
            fontSize: 10,
            color: COLORS.muted,
            marginTop: 2,
          }}>
            Distribución de precios futuros · {data.length} horizontes
          </div>
        </div>
        <div style={{
          fontSize: 11,
          color: COLORS.muted,
          whiteSpace: 'nowrap',
          display: 'flex',
          alignItems: 'center',
          gap: 8,
        }}>
          <span>Spot</span>
          <span style={{
            color: COLORS.text,
            fontFamily: 'monospace',
            fontWeight: 600,
            fontSize: 14,
          }}>
            {formatPrice(currentPrice)}
          </span>
        </div>
      </div>

      {/* Chart */}
      <div style={{ height: isMobile ? 220 : 340, width: '100%' }}>
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart
            data={chartData}
            margin={{ top: 8, right: 16, left: 4, bottom: 8 }}
          >
            <defs>
              <linearGradient id="fanOuter" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#2563EB" stopOpacity={0.08} />
                <stop offset="40%" stopColor="#3B82F6" stopOpacity={0.14} />
                <stop offset="100%" stopColor="#2563EB" stopOpacity={0.02} />
              </linearGradient>
              <linearGradient id="fanInner" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#60A5FA" stopOpacity={0.12} />
                <stop offset="40%" stopColor="#3B82F6" stopOpacity={0.22} />
                <stop offset="100%" stopColor="#60A5FA" stopOpacity={0.04} />
              </linearGradient>
            </defs>

            <CartesianGrid
              stroke={COLORS.grid}
              strokeDasharray="3 5"
              vertical={false}
            />

            <XAxis
              dataKey="date"
              tickFormatter={formatDate}
              tick={{
                fill: COLORS.muted,
                fontSize: isMobile ? 8 : 10,
              }}
              axisLine={false}
              tickLine={false}
              dy={6}
            />

            <YAxis
              domain={[allPrices.min, allPrices.max]}
              tick={{
                fill: COLORS.muted,
                fontSize: isMobile ? 8 : 10,
              }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v: number) => v.toFixed(2)}
              width={isMobile ? 45 : 60}
            />

            <Tooltip content={<FanTooltip />} />

            {/* Bandas */}
            <Area type="monotone" dataKey="p90" stroke="none" fill="url(#fanOuter)" connectNulls isAnimationActive={false} />
            <Area type="monotone" dataKey="p10" stroke="none" fill="url(#fanOuter)" connectNulls isAnimationActive={false} />
            <Area type="monotone" dataKey="p75" stroke="none" fill="url(#fanInner)" connectNulls isAnimationActive={false} />
            <Area type="monotone" dataKey="p25" stroke="none" fill="url(#fanInner)" connectNulls isAnimationActive={false} />

            {/* Líneas P10-P90 */}
            <Line type="monotone" dataKey="p10" stroke={COLORS.bandOuterStroke} strokeWidth={1} strokeOpacity={0.3} strokeDasharray="4 4" dot={false} connectNulls isAnimationActive={false} />
            <Line type="monotone" dataKey="p90" stroke={COLORS.bandOuterStroke} strokeWidth={1} strokeOpacity={0.3} strokeDasharray="4 4" dot={false} connectNulls isAnimationActive={false} />

            {/* Líneas P25-P75 */}
            <Line type="monotone" dataKey="p25" stroke={COLORS.bandMidStroke} strokeWidth={1.2} strokeOpacity={0.5} dot={false} connectNulls isAnimationActive={false} />
            <Line type="monotone" dataKey="p75" stroke={COLORS.bandMidStroke} strokeWidth={1.2} strokeOpacity={0.5} dot={false} connectNulls isAnimationActive={false} />

            {/* P50 - Línea principal */}
            <Line
              type="monotone"
              dataKey="p50"
              stroke={COLORS.median}
              strokeWidth={3}
              strokeOpacity={0.95}
              dot={false}
              activeDot={{ r: 6, fill: COLORS.median, stroke: COLORS.panel, strokeWidth: 2 }}
              connectNulls
              isAnimationActive={false}
            />

            {/* Separador NOW */}
            <ReferenceLine
              x={currentDate}
              stroke="rgba(255,255,255,0.12)"
              strokeDasharray="4 6"
              strokeWidth={1.5}
              label={{
                value: 'NOW',
                fill: COLORS.muted,
                fontSize: 9,
                position: 'top',
                opacity: 0.6,
              }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Footer con métricas */}
      {data.length > 0 && (
        <div style={{
          marginTop: 8,
          padding: '10px 14px',
          background: 'rgba(255,255,255,0.02)',
          borderRadius: 8,
          border: `1px solid ${COLORS.border}`,
          display: 'flex',
          gap: 20,
          flexWrap: 'wrap',
          fontSize: 10,
          color: COLORS.muted,
        }}>
          <div>
            <span>🎯 Mediana (P50): </span>
            <span style={{ color: COLORS.median, fontFamily: 'monospace', fontWeight: 600 }}>
              {formatPrice(data[data.length - 1]?.p50 || 0)}
            </span>
          </div>
          <div>
            <span>📊 50% CI: </span>
            <span style={{ color: '#60A5FA', fontFamily: 'monospace' }}>
              {formatPrice(data[data.length - 1]?.p25 || 0)} — {formatPrice(data[data.length - 1]?.p75 || 0)}
            </span>
          </div>
          <div>
            <span>📈 80% CI: </span>
            <span style={{ color: '#93C5FD', fontFamily: 'monospace' }}>
              {formatPrice(data[data.length - 1]?.p10 || 0)} — {formatPrice(data[data.length - 1]?.p90 || 0)}
            </span>
          </div>
          <div>
            <span>📅 Horizontes: </span>
            <span style={{ color: COLORS.text, fontFamily: 'monospace' }}>
              {data.map((d) => d.date.slice(5)).join(' · ')}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
