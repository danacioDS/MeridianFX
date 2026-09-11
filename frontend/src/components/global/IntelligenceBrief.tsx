/**
 * IntelligenceBrief — System-wide narrative from /v1/market-intelligence.
 *
 * ⚠️  Presentational ONLY. All values come from the backend.
 */
import { Panel } from "../common";

interface IntelligenceBriefProps {
  context?: string;
  interpretations?: string[];
}

export function IntelligenceBrief({
  context,
  interpretations,
}: IntelligenceBriefProps): JSX.Element | null {
  const hasContext = Boolean(context && context.trim());
  const hasInterps = Boolean(interpretations && interpretations.length > 0);

  if (!hasContext && !hasInterps) {
    return null;
  }

  return (
    <Panel title="🧠 Intelligence Brief">
      <div className="space-y-4">
        {hasContext && (
          <div>
            <div className="text-xs uppercase tracking-wider text-muted mb-2">
              Context
            </div>
            <p className="text-sm text-ink-soft leading-relaxed">
              {context}
            </p>
          </div>
        )}

        {hasInterps && (
          <div className={hasContext ? "border-t border-line pt-4" : ""}>
            <div className="text-xs uppercase tracking-wider text-muted mb-2">
              Model Interpretation
            </div>
            <ul className="list-disc pl-5 space-y-2 text-sm text-ink-soft">
              {interpretations!.map((line, idx) => (
                <li key={idx}>{line}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </Panel>
  );
}
