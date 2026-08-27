/**
 * Probability gauge — presentational only.
 *
 * Renders a probability (0..1) as a visual bar and a formatted percentage.
 * The bar is a visual mapping of an already-authorized contract value —
 * no calculation is performed.
 */
import { formatProbability } from "../../utils";

interface ProbabilityGaugeProps {
  /** Backend probability (0..1) or null when unavailable. */
  probability?: number | null;
  /** Render label. */
  label?: string;
}

export function ProbabilityGauge({ probability, label = "Probability" }: ProbabilityGaugeProps): JSX.Element {
  const clamp01 = (value: number | null | undefined): number => {
    if (value == null) return 0;
    return Math.max(0, Math.min(1, value)); // visual bound only; never a re-derivation
  };

  if (probability == null) {
    return (
      <div className="rounded-lg border border-border bg-surface p-4 text-xs text-text-secondary">
        {label}: —
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-baseline justify-between">
        <span className="text-xs text-text-secondary">{label}</span>
        <span className="text-sm font-semibold text-text-primary">
          {formatProbability(probability)}
        </span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-background">
        <div
          className="h-full rounded-full bg-primary transition-[width] duration-300"
          style={{ width: `${Math.round(clamp01(probability) * 100)}%` }}
        />
      </div>
    </div>
  );
}