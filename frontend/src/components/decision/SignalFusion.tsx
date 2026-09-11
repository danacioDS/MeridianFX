/**
 * SignalFusion — Weights and result of the signal fusion step.
 *
 * ⚠️  Presentational ONLY. All values come from the backend fusion.* block.
 */
interface FusionWeights {
  quant: number;
  macro: number;
  rag: number;
}

interface SignalFusionProps {
  weights: FusionWeights;
  fusionScore: number;
  direction: string;
  directionSign: number;
}

interface WeightBarProps {
  label: string;
  value: number;
  color: string;
}

function WeightBar({ label, value, color }: WeightBarProps): JSX.Element {
  const pct = Math.max(0, Math.min(1, value)) * 100;

  return (
    <div className="space-y-1">
      <div className="flex justify-between items-baseline text-sm">
        <span className="text-muted">{label}</span>
        <span className="font-mono text-ink-soft">{value.toFixed(2)}</span>
      </div>
      <div className="w-full h-2 bg-panel-2 rounded-full overflow-hidden">
        <div
          className={`h-full ${color} rounded-full transition-all`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

export function SignalFusion({
  weights,
  fusionScore,
  direction,
  directionSign,
}: SignalFusionProps): JSX.Element {
  const isLong = directionSign > 0;
  const directionColor = isLong ? "text-bull" : "text-bear";

  return (
    <div className="space-y-5">
      {/* Weight bars */}
      <div className="space-y-3">
        <WeightBar label="Quant" value={weights.quant} color="bg-violet" />
        <WeightBar label="Macro" value={weights.macro} color="bg-meridian" />
        <WeightBar label="RAG" value={weights.rag} color="bg-amber" />
      </div>

      {/* Fusion result */}
      <div className="border-t border-line pt-3 grid grid-cols-2 gap-3">
        <div className="bg-panel-2 rounded-lg p-3 border border-line">
          <div className="text-xs text-muted">Fusion Score</div>
          <div
            className={`text-lg font-bold font-mono mt-1 ${
              fusionScore >= 0 ? "text-bull" : "text-bear"
            }`}
          >
            {fusionScore >= 0 ? "+" : ""}
            {fusionScore.toFixed(3)}
          </div>
        </div>

        <div className="bg-panel-2 rounded-lg p-3 border border-line">
          <div className="text-xs text-muted">Direction</div>
          <div className={`text-lg font-bold mt-1 ${directionColor}`}>
            {isLong ? "▲" : "▼"} {direction}
          </div>
          <div className="text-[10px] text-muted font-mono mt-0.5">
            sign: {directionSign > 0 ? "+1" : "-1"}
          </div>
        </div>
      </div>
    </div>
  );
}
