/**
 * QualityMetrics — Decision quality score and its components.
 *
 * ⚠️  Presentational ONLY. All values come from the backend quality.* block.
 */
interface QualityComponents {
  confidence: number;
  freshness: number;
  regime_alignment: number;
  data_quality: string;
  data_quality_score: number;
  drift_score: number;
}

interface QualityMetricsProps {
  score: number;
  level: string;
  components: QualityComponents;
  fallbackStatus: Record<string, string>;
}

interface MetricBarProps {
  label: string;
  value: number;
  badge?: JSX.Element;
}

function StubBadge(props: { tooltip: string }): JSX.Element {
  return (
    <span
      title={props.tooltip}
      className="text-[10px] font-mono px-1.5 py-0.5 rounded-full bg-amber-soft text-amber cursor-help"
    >
      ⚠ STUB
    </span>
  );
}

function MetricBar({ label, value, badge }: MetricBarProps): JSX.Element {
  const pct = Math.max(0, Math.min(1, value)) * 100;

  return (
    <div className="space-y-1">
      <div className="flex justify-between items-baseline text-sm">
        <span className="text-muted flex items-center gap-1.5">
          {label}
          {badge}
        </span>
        <span className="font-mono text-ink-soft">{value.toFixed(2)}</span>
      </div>
      <div className="w-full h-2 bg-panel-2 rounded-full overflow-hidden">
        <div
          className="h-full bg-meridian rounded-full transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

const LEVEL_STYLES: Record<string, string> = {
  HIGH: "bg-bull-soft text-bull",
  MODERATE: "bg-amber-soft text-amber",
  LOW: "bg-bear-soft text-bear",
};

export function QualityMetrics({
  score,
  level,
  components,
  fallbackStatus,
}: QualityMetricsProps): JSX.Element {
  const levelStyles = LEVEL_STYLES[level] ?? "bg-panel-2 text-muted";
  const fallbackEntries = Object.entries(fallbackStatus);

  return (
    <div className="space-y-5">
      {/* Header: score + level badge */}
      <div className="flex items-center justify-between">
        <div className="flex items-baseline gap-3">
          <span className="text-3xl font-bold font-mono text-ink">
            {score.toFixed(2)}
          </span>
          <span className="text-xs text-muted">overall score</span>
        </div>
        <span
          className={`text-xs font-semibold px-3 py-1 rounded-full ${levelStyles}`}
        >
          {level}
        </span>
      </div>

      {/* Component bars */}
      <div className="space-y-3">
        <MetricBar label="Confidence" value={components.confidence} />
        <MetricBar
          label="Freshness"
          value={components.freshness}
          badge={<StubBadge tooltip="Placeholder value, not a live measurement — see README Current Limitations." />}
        />
        <MetricBar
          label="Regime Alignment"
          value={components.regime_alignment}
        />
        <MetricBar
          label="Data Quality"
          value={components.data_quality_score}
          badge={<StubBadge tooltip="Placeholder value, not a live measurement — see README Current Limitations." />}
        />
        <MetricBar
          label="Drift Score"
          value={components.drift_score}
          badge={<StubBadge tooltip="Placeholder value, not a live measurement — see README Current Limitations." />}
        />
      </div>

      {/* Data quality label — `data_quality` is a backend categorical state
          (good / acceptable / degraded). The NUMERIC score above it is the
          placeholder; the badge clarifies which part is stubbed. */}
      <div className="text-xs text-muted flex items-center gap-2 flex-wrap">
        <span>
          Data Quality:{" "}
          <span className="text-ink font-medium">{components.data_quality}</span>
        </span>
        <span
          title="The numeric score above is a placeholder. `data_quality` (good/acceptable/degraded) is a backend state — see README Current Limitations."
          className="text-[10px] font-mono px-1.5 py-0.5 rounded-full bg-amber-soft text-amber cursor-help"
        >
          ⚠ STUB SCORE
        </span>
      </div>

      {/* Fallback status badges */}
      {fallbackEntries.length > 0 && (
        <div className="border-t border-line pt-3">
          <div className="text-xs uppercase tracking-wider text-muted mb-2">
            Fallback Status
          </div>
          <div className="flex flex-wrap gap-2">
            {fallbackEntries.map(([key, status]) => {
              const isOk = status === "VALID";
              return (
                <span
                  key={key}
                  className={`text-[11px] font-mono px-2 py-0.5 rounded-full ${
                    isOk
                      ? "bg-bull-soft text-bull"
                      : "bg-amber-soft text-amber"
                  }`}
                >
                  {key}: {status}
                </span>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
