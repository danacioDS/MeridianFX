/**
 * Regime Strip - Risk-On/Off con VIX y métricas
 * Diseño del mockup + datos reales (si están disponibles)
 */
interface RegimeStripProps {
  regime: string;
  vix?: number;
  riskAppetite?: number;
}

export function RegimeStrip({ regime, vix, riskAppetite }: RegimeStripProps) {
  const isRiskOn = regime?.toLowerCase().includes('risk-on') || regime?.toLowerCase().includes('on');
  const bgColor = isRiskOn ? '#16233F' : '#2A1F1F';
  const pillColor = isRiskOn ? '#0E8F5F' : '#C4453A';
  const pillText = isRiskOn ? '🟢 Risk-On' : '🔴 Risk-Off';
  
  return (
    <div
      className="flex items-center justify-between rounded-xl px-5 py-3 mb-4 flex-wrap gap-2"
      style={{ background: bgColor, color: '#fff' }}
    >
      <div className="flex items-center gap-3">
        <span
          className="text-xs uppercase tracking-wider px-3 py-1 rounded-full border border-white/20"
          style={{ background: 'rgba(255,255,255,0.1)', color: pillColor }}
        >
          {pillText}
        </span>
        <span className="text-sm text-white/80">Régimen de mercado confirmado</span>
      </div>
      
      <div className="flex gap-6 text-sm text-white/70">
        {vix !== undefined && (
          <span>
            VIX <b className="text-white font-mono">{vix.toFixed(1)}</b>
          </span>
        )}
        {riskAppetite !== undefined && (
          <span>
            Apetito de riesgo <b className="text-white font-mono">{(riskAppetite * 100).toFixed(0)}%</b>
            {riskAppetite > 0.6 ? ' ↑' : ' ↓'}
          </span>
        )}
        {!vix && !riskAppetite && (
          <span className="text-white/40 text-xs">
            Datos no disponibles
          </span>
        )}
      </div>
    </div>
  );
}
