/**
 * TrendCard — Muestra tendencias por período
 */
interface TrendCardProps {
  trends: {
    "1m": { return: number; direction: string; strength: number };
    "3m": { return: number; direction: string; strength: number };
    "6m": { return: number; direction: string; strength: number };
    "1y": { return: number; direction: string; strength: number };
  };
}

export function TrendCard({ trends }: TrendCardProps): JSX.Element {
  const periods = [
    { key: "1m", label: "1 Mes" },
    { key: "3m", label: "3 Meses" },
    { key: "6m", label: "6 Meses" },
    { key: "1y", label: "1 Año" },
  ];

  return (
    <div className="grid grid-cols-4 gap-2">
      {periods.map((p) => {
        const data = trends[p.key as keyof typeof trends];
        if (!data) return null;
        const isUp = data.direction === "UP";
        return (
          <div key={p.key} className="text-center p-2 bg-panel-2 rounded-lg">
            <div className="text-xs text-muted">{p.label}</div>
            <div className={`text-sm font-bold ${isUp ? 'text-bull' : 'text-bear'}`}>
              {isUp ? '+' : ''}{data.return}%
            </div>
            <div className="text-xs text-muted">{isUp ? '▲' : '▼'}</div>
          </div>
        );
      })}
    </div>
  );
}
