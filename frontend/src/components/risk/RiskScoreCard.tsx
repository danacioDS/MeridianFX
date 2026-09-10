/**
 * RiskScoreCard — Canonical Risk Score presentation.
 *
 * ⚠️  Presentational ONLY. Does NOT compute score or level.
 *     All values come from the backend (RiskEngine v2.3.0).
 */
import type { RiskLevel } from "../../hooks/useCanonicalRisk";

interface RiskScoreCardProps {
  score: number;
  level: RiskLevel;
  methodologyVersion: string;
}

const LEVEL_STYLES: Record<RiskLevel, { label: string; color: string; bg: string; border: string }> = {
  LOW:      { label: "LOW",      color: "text-bull",   bg: "bg-bull/10",   border: "border-bull/40" },
  MODERATE: { label: "MODERATE", color: "text-amber",  bg: "bg-amber/10",  border: "border-amber/40" },
  HIGH:     { label: "HIGH",     color: "text-bear",   bg: "bg-bear/10",   border: "border-bear/40" },
  EXTREME:  { label: "EXTREME",  color: "text-violet", bg: "bg-violet/10", border: "border-violet/40" },
};

export function RiskScoreCard({ score, level, methodologyVersion }: RiskScoreCardProps): JSX.Element {
  const styles = LEVEL_STYLES[level] ?? LEVEL_STYLES.MODERATE;

  return (
    <div className={`rounded-lg border ${styles.border} ${styles.bg} p-6`}>
      <div className="flex flex-col items-center justify-center gap-2">
        <div className="text-xs uppercase tracking-wider text-muted">Risk Score</div>
        <div className={`text-5xl font-bold font-mono ${styles.color}`}>
          {score.toFixed(2)}
        </div>
        <div className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${styles.color} ${styles.bg} border ${styles.border}`}>
          {styles.label}
        </div>
        <div className="text-xs text-muted mt-2">
          Methodology {methodologyVersion}
        </div>
      </div>
    </div>
  );
}
