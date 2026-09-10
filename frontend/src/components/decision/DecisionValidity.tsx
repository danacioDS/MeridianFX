/**
 * DecisionValidity — Signal validity + rejection reason.
 *
 * ⚠️  Presentational ONLY.
 */
interface DecisionValidityProps {
  signalValidity: string;    // VALID | DEGRADED | UNAVAILABLE
  rejectionReason: string | null;
}

const VALIDITY_STYLES: Record<string, { color: string; bg: string; border: string; icon: string; description: string }> = {
  VALID: {
    color: "text-bull", bg: "bg-bull/10", border: "border-bull/40", icon: "✅",
    description: "All hard gates passed. The signal is actionable under current conditions.",
  },
  DEGRADED: {
    color: "text-amber", bg: "bg-amber/10", border: "border-amber/40", icon: "⚠️",
    description: "Signal is actionable but with degraded quality. Review the rejection reason.",
  },
  UNAVAILABLE: {
    color: "text-muted", bg: "bg-panel-2", border: "border-line", icon: "⏸",
    description: "Signal is not actionable. One or more hard gates failed.",
  },
};

export function DecisionValidity({
  signalValidity,
  rejectionReason,
}: DecisionValidityProps): JSX.Element {
  const styles = VALIDITY_STYLES[signalValidity] ?? VALIDITY_STYLES.UNAVAILABLE;

  return (
    <div className={`rounded-lg border ${styles.border} ${styles.bg} p-4`}>
      <div className="flex items-center gap-3">
        <span className="text-2xl">{styles.icon}</span>
        <div>
          <div className={`font-semibold ${styles.color}`}>
            Signal Validity: {signalValidity}
          </div>
          <div className="text-sm text-muted mt-1">
            {styles.description}
          </div>
        </div>
      </div>

      {rejectionReason && (
        <div className="mt-3 pt-3 border-t border-line">
          <div className="text-xs uppercase tracking-wider text-muted">Rejection reason</div>
          <div className="text-sm text-amber mt-1 font-mono">
            {rejectionReason}
          </div>
        </div>
      )}
    </div>
  );
}
