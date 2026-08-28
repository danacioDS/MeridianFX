/**
 * Pipeline Stepper - Modelo → Filtro → Accionable
 * Diseño del mockup + datos reales
 */
interface PipelineStepperProps {
  direction: string;
  probability: number;
  netReturn: number;
  edgeRatio: number;
  actionable: boolean;
  confidence: number;
}

export function PipelineStepper({
  direction,
  probability,
  netReturn,
  edgeRatio,
  actionable,
  confidence
}: PipelineStepperProps) {
  const isBullish = direction === 'UP';
  const color = isBullish ? '#0E8F5F' : '#C4453A';
  const bgColor = isBullish ? '#E7F5EE' : '#FBEAE8';
  
  const steps = [
    {
      label: 'Model Output',
      value: `${Math.round(probability * 100)}% ${isBullish ? '▲' : '▼'} ${direction}`,
      color: color,
      bg: bgColor
    },
    {
      label: 'Economic Filter',
      value: `Net ${(netReturn * 100).toFixed(2)}% · Edge ${edgeRatio.toFixed(2)}x`,
      color: color,
      bg: bgColor
    },
    {
      label: 'Actionability',
      value: actionable ? '🟢 ACTIONABLE' : '🔴 NOT ACTIONABLE',
      color: actionable ? '#0E8F5F' : '#C4453A',
      bg: actionable ? '#E7F5EE' : '#FBEAE8'
    },
    {
      label: 'Final Signal',
      value: actionable ? `${isBullish ? '🟢 BULLISH' : '🔴 BEARISH'}` : '⏸️ HOLD',
      color: actionable ? color : '#8891A0',
      bg: actionable ? bgColor : '#F2F4F7'
    }
  ];
  
  return (
    <div className="flex items-center gap-0 flex-wrap">
      {steps.map((step, index) => (
        <div key={index} className="flex items-center">
          <div
            className="flex flex-col gap-1 px-4 py-3 rounded-lg flex-1 min-w-[120px]"
            style={{ background: step.bg, border: `1px solid ${step.color}` }}
          >
            <span className="text-[10px] uppercase tracking-wider text-muted">
              {step.label}
            </span>
            <span className="font-mono text-sm font-semibold" style={{ color: step.color }}>
              {step.value}
            </span>
            {index === steps.length - 1 && confidence > 0 && (
              <span className="text-[10px] text-muted">
                Confidence: {Math.round(confidence * 100)}%
              </span>
            )}
          </div>
          {index < steps.length - 1 && (
            <span className="text-muted px-2 text-sm">→</span>
          )}
        </div>
      ))}
    </div>
  );
}
