/**
 * SHAP Bar - Contribuciones visuales con colores +/−
 * Diseño del mockup + datos reales de DriversResponse
 */
interface SHAPContribution {
  feature: string;
  contribution: number;
  rank: number;
}

interface SHAPBarProps {
  contributions: SHAPContribution[];
  maxContributions?: number;
}

export function SHAPBar({ contributions, maxContributions = 10 }: SHAPBarProps) {
  if (!contributions || contributions.length === 0) {
    return (
      <div className="text-center py-8 text-muted">
        <p className="text-sm">No SHAP contributions available</p>
        <p className="text-xs">Model has not generated explanations</p>
      </div>
    );
  }
  
  const top = contributions.slice(0, maxContributions);
  const maxAbs = Math.max(...top.map(c => Math.abs(c.contribution)), 0.01);
  
  return (
    <div className="space-y-3">
      {top.map((item) => {
        const isPositive = item.contribution >= 0;
        const pct = Math.abs(item.contribution) / maxAbs * 100;
        const color = isPositive ? '#0E8F5F' : '#C4453A';
        
        return (
          <div key={item.rank} className="space-y-1">
            <div className="flex items-baseline justify-between text-sm">
              <span className="font-medium text-ink">
                <span className="text-muted font-mono mr-2">#{item.rank}</span>
                {item.feature}
              </span>
              <span className="font-mono" style={{ color }}>
                {isPositive ? '+' : ''}{item.contribution.toFixed(3)}
              </span>
            </div>
            <div className="h-2 w-full rounded-full overflow-hidden" style={{ background: '#F2F4F7' }}>
              <div
                className="h-full rounded-full transition-all"
                style={{
                  width: `${Math.max(pct, 2)}%`,
                  background: color,
                  opacity: 0.85
                }}
              />
            </div>
            <div className="text-xs text-muted font-mono">
              {isPositive ? 'Contribución positiva' : 'Contribución negativa'}
            </div>
          </div>
        );
      })}
    </div>
  );
}
