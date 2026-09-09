/**
 * SpotCard — Muestra precio actual y cambio
 */
interface SpotCardProps {
  spot: {
    price: number;
    previous: number;
    change_abs: number;
    change_pct: number;
  };
  pair: string;
  last_date: string;
  source: string;
}

export function SpotCard({ spot, pair, last_date, source }: SpotCardProps): JSX.Element {
  const isUp = spot.change_pct >= 0;

  return (
    <div className="flex flex-wrap items-center justify-between p-4 bg-panel-2 rounded-lg border border-line">
      <div>
        <div className="text-sm text-muted">{pair}</div>
        <div className="text-3xl font-bold text-ink">{spot.price.toFixed(4)}</div>
        <div className="text-xs text-muted">Última actualización: {last_date}</div>
        <div className="text-xs text-muted">Fuente: {source}</div>
      </div>
      <div className="text-right">
        <div className={`text-2xl font-bold ${isUp ? 'text-bull' : 'text-bear'}`}>
          {isUp ? '▲' : '▼'} {isUp ? '+' : ''}{spot.change_pct.toFixed(2)}%
        </div>
        <div className={`text-sm ${isUp ? 'text-bull' : 'text-bear'}`}>
          {isUp ? '+' : ''}{spot.change_abs.toFixed(4)}
        </div>
        <div className="text-xs text-muted">vs día anterior</div>
      </div>
    </div>
  );
}
