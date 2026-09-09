/**
 * ForecastCard — Muestra predicciones por horizonte
 */
interface ForecastCardProps {
  forecasts: {
    "30d": { direction: string; probability: number; expected_return: number; current_price: number; ci_95_lower: number; ci_95_upper: number };
    "60d": { direction: string; probability: number; expected_return: number; current_price: number; ci_95_lower: number; ci_95_upper: number };
    "90d": { direction: string; probability: number; expected_return: number; current_price: number; ci_95_lower: number; ci_95_upper: number };
  };
  currentPrice: number;
}

export function ForecastCard({ forecasts, currentPrice }: ForecastCardProps): JSX.Element {
  const horizons = [
    { key: "30d", label: "30 Días" },
    { key: "60d", label: "60 Días" },
    { key: "90d", label: "90 Días" },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {horizons.map((h) => {
        const data = forecasts[h.key as keyof typeof forecasts];
        if (!data) return null;
        const isUp = data.direction === "UP";
        const probability = data.probability || 0.5;

        return (
          <div key={h.key} className="p-4 bg-panel-2 rounded-lg border border-line">
            <div className="text-xs text-muted">{h.label}</div>
            <div className={`text-lg font-bold ${isUp ? 'text-bull' : 'text-bear'}`}>
              {isUp ? '▲' : '▼'} {data.expected_return}%
            </div>
            <div className="text-sm text-ink-soft">Confianza: {(probability * 100).toFixed(1)}%</div>
            <div className="text-xs text-muted mt-2">
              Precio esperado: {(currentPrice * (1 + data.expected_return / 100)).toFixed(4)}
            </div>
            <div className="text-xs text-muted">
              IC 95%: {data.ci_95_lower.toFixed(4)} — {data.ci_95_upper.toFixed(4)}
            </div>
          </div>
        );
      })}
    </div>
  );
}
