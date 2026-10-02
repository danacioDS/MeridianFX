/**
 * Architecture Control Center — runtime state of the four-layer pipeline.
 *
 * Consumes: GET /v1/system/trace?pair={pair}
 *
 * This page does not compute anything. It only renders the truth
 * reported by the backend, including explicit failure states.
 */
import { useState } from "react";
import { Panel } from "../components/common";
import { useSystemTrace } from "../hooks/useSystemTrace";
import { LayerColumn } from "../components/architecture/LayerColumn";
import type { FinalVerdict } from "../types/system";

const PAIRS = [
  "USD/CHF",
  "USD/MXN",
  "EUR/USD",
  "GBP/USD",
  "USD/JPY",
  "USD/BRL",
  "USD/CNY",
  "USD/ARS",
  "USD/BOB",
];

const VERDICT_STYLE: Record<FinalVerdict, string> = {
  ACTIONABLE: "bg-green-100 text-green-800",
  DEGRADED: "bg-amber-100 text-amber-800",
  UNAVAILABLE: "bg-red-100 text-red-800",
};

export function ArchitecturePage(): JSX.Element {
  const [pair, setPair] = useState("USD/CHF");
  const { data, isLoading, error } = useSystemTrace(pair);

  if (isLoading) {
    return (
      <section className="max-w-6xl mx-auto py-12 text-center text-ink-soft">
        Loading trace for {pair}…
      </section>
    );
  }

  if (error || !data) {
    return (
      <section className="max-w-6xl mx-auto py-12 text-center text-red-600">
        Failed to load trace for {pair}.
      </section>
    );
  }

  return (
    <section className="flex flex-col gap-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="text-center py-6 border-b border-line">
        <h1 className="font-serif text-4xl tracking-wide">
          Architecture Control Center
        </h1>
        <p className="text-ink-soft mt-2">
          Runtime state of the four-layer pipeline
        </p>
        <div className={`mt-4 inline-block px-4 py-2 rounded-full font-mono text-sm font-semibold ${VERDICT_STYLE[data.final]}`}>
          FINAL: {data.final} · {data.findings.length} findings
        </div>
      </div>

      {/* Pair selector */}
      <Panel title="Pair">
        <div className="flex items-center gap-4">
          <select
            value={pair}
            onChange={(e) => setPair(e.target.value)}
            className="font-mono text-sm px-3 py-2 border border-line rounded bg-surface"
          >
            {PAIRS.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
          <span className="text-sm text-ink-soft">
            Trace recomputed on selection
          </span>
        </div>
      </Panel>

      {/* Four columns */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <LayerColumn layer={data.detail.data} />
        <LayerColumn layer={data.detail.research} />
        <LayerColumn layer={data.detail.decision} />
        <LayerColumn layer={data.detail.intelligence} />
      </div>

      {/* Findings summary */}
      {data.findings.length > 0 && (
        <Panel title="Open findings">
          <ul className="font-mono text-sm space-y-1">
            {data.findings.map((f) => (
              <li key={f} className="text-red-700">
                ✗ {f}
              </li>
            ))}
          </ul>
        </Panel>
      )}

      {/* Decision detail */}
      {data.detail.decision.decision.direction && (
        <Panel title="Decision detail">
          <dl className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm font-mono">
            <div>
              <dt className="text-ink-soft text-xs uppercase">Direction</dt>
              <dd>{data.detail.decision.decision.direction}</dd>
            </div>
            <div>
              <dt className="text-ink-soft text-xs uppercase">Confidence</dt>
              <dd>{data.detail.decision.decision.confidence?.toFixed(4) ?? "—"}</dd>
            </div>
            <div>
              <dt className="text-ink-soft text-xs uppercase">Net return</dt>
              <dd>{data.detail.decision.economic.net_return?.toFixed(2) ?? "—"}</dd>
            </div>
            <div>
              <dt className="text-ink-soft text-xs uppercase">Edge ratio</dt>
              <dd>{data.detail.decision.economic.edge_ratio?.toFixed(2) ?? "—"}</dd>
            </div>
          </dl>
        </Panel>
      )}
    </section>
  );
}
