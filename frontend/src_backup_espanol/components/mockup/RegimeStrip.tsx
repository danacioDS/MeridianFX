interface RegimeStripProps {
  regime: string;
  vix: number;
  riskAppetite: number;
}

export function RegimeStrip({ regime, vix, riskAppetite }: RegimeStripProps): JSX.Element {
  const isRiskOn = regime === 'RISK_ON' || regime === 'RISK-ON';
  const regimeLabel = isRiskOn ? 'Risk-On' : 'Risk-Off';
  const regimeEmoji = isRiskOn ? '🟢' : '🔴';

  return (
    <div className="bg-[#16233F] text-white rounded-xl px-5 py-3.5 flex items-center justify-between flex-wrap gap-2 text-sm">
      <div className="flex items-center gap-3">
        <span className={`border border-white/20 px-3 py-1 rounded-full text-xs uppercase tracking-wide ${
          isRiskOn ? 'bg-green-500/20' : 'bg-red-500/20'
        }`}>
          {regimeEmoji} {regimeLabel}
        </span>
        <span>Régimen de mercado confirmado</span>
      </div>
      <div className="flex gap-5 text-white/75 text-sm">
        <span>VIX <b className="text-white font-mono font-medium">{vix}</b></span>
        <span>Apetito de riesgo <b className="text-white font-mono font-medium">{(riskAppetite * 100).toFixed(0)}% ↑</b></span>
      </div>
    </div>
  );
}
