/**
 * DecisionProvenance — Traceability block for a canonical decision.
 *
 * Answers the five questions that make a decision auditable:
 *   WHO DECIDED      — pair, horizon
 *   WHAT WAS DECIDED — direction, actionable, validity
 *   WITH WHAT EVIDENCE — edge, threshold, net return
 *   WITH WHAT MODEL  — model_id, model_version
 *   WITH WHAT DATA   — dataset, feature version, macro status
 *
 * ⚠️  Presentational ONLY. All values come from the canonical contract.
 */
import type { CanonicalDecision } from "../../hooks/useCanonicalDecision";

interface DecisionProvenanceProps {
  decision: CanonicalDecision;
}

interface SectionProps {
  title: string;
  hint: string;
  children: React.ReactNode;
}

function Section({ title, hint, children }: SectionProps) {
  return (
    <div className="space-y-1.5">
      <div className="text-[10px] uppercase tracking-wider text-muted">
        {title}
      </div>
      <div className="text-[11px] text-muted italic">{hint}</div>
      <div className="space-y-1 text-sm">{children}</div>
    </div>
  );
}

interface RowProps {
  label: string;
  value: string | number | null | undefined;
  mono?: boolean;
  small?: boolean;
}

function Row({ label, value, mono, small }: RowProps) {
  const isEmpty = value === null || value === undefined || value === "";
  const display = isEmpty ? "—" : String(value);
  return (
    <div className="flex items-baseline justify-between gap-3">
      <span className="text-xs text-muted">{label}</span>
      <span
        className={`text-ink ${mono ? "font-mono" : ""} ${
          small ? "text-[10px]" : "text-sm"
        }`}
      >
        {display}
      </span>
    </div>
  );
}

export function DecisionProvenance({
  decision,
}: DecisionProvenanceProps): JSX.Element {
  const d = decision.decision;
  const a = decision.artifact;
  const e = decision.economic;
  const m = decision.macro_data_status;

  const fmtEdge = (v: number | null | undefined) =>
    v === null || v === undefined ? null : `${v.toFixed(2)}×`;
  const fmtBps = (v: number | null | undefined) =>
    v === null || v === undefined ? null : `${v.toFixed(2)} bps`;

  return (
    <div className="rounded-xl border border-line bg-panel-2 p-6">
      <div className="text-xs uppercase tracking-wider text-muted mb-4">
        🔍 Decision Provenance
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Section
          title="Who decided"
          hint="Which pair and what horizon this decision applies to."
        >
          <Row label="Pair" value={d.pair} />
          <Row label="Horizon" value={`${d.horizon_days} days`} />
        </Section>

        <Section
          title="What was decided"
          hint="The system's final classification of the signal."
        >
          <Row label="Direction" value={d.direction} />
          <Row label="Actionable" value={d.actionable ? "YES" : "NO"} />
          <Row label="Validity" value={d.signal_validity} />
        </Section>

        <Section
          title="With what evidence"
          hint="The economic edge that justifies (or rejects) the decision."
        >
          <Row label="Edge ratio" value={fmtEdge(e?.edge_ratio)} mono />
          <Row
            label="Required minimum"
            value={fmtEdge(e?.required_minimum_edge)}
            mono
          />
          <Row label="Net return" value={fmtBps(e?.net_return)} mono />
        </Section>

        <Section
          title="With what model"
          hint="The ML model that produced the underlying prediction."
        >
          <Row label="Model" value={a.model_id} mono small />
          <Row label="Version" value={a.model_version} mono />
          <Row label="Features" value={`${a.shap_values?.length ?? "—"}`} />
        </Section>

        <Section
          title="With what data"
          hint="The dataset, features, and macro context used by the model."
        >
          <Row label="Dataset" value={a.dataset_id} mono small />
          <Row label="Feature version" value={a.feature_version} mono />
          <Row label="Macro status" value={m?.status} />
        </Section>

        <Section
          title="Decision time"
          hint="Timestamps and identifiers for audit and debugging."
        >
          <Row label="Timestamp" value={d.timestamp} mono small />
          <Row label="As of" value={d.as_of} mono small />
          <Row label="Decision ID" value={d.decision_id} mono small />
          <Row label="Prediction ID" value={d.prediction_id} mono small />
        </Section>
      </div>
    </div>
  );
}
