/**
 * DecisionPage — Canonical Decision & Sizing (v2.3).
 *
 * Consumes: GET /v1/canonical/{pair}/decision?horizon_days={h}
 *
 * ⚠️  This page is PRESENTATIONAL ONLY.
 *     It does NOT compute direction, confidence, edge, sizing, or SHAP.
 *     All analytical values come from the backend.
 */
import { safeToFixed } from "../utils/safeFormat";
import {
  ApiError,
  LoadingSpinner,
  Panel,
  UniverseSelector,
} from "../components/common";
import { ActionableInfo } from "../components/global";
import { ModelExplanation } from "../components/global";
import {
  DecisionHero,
  DecisionMetrics,
  DecisionValidity,
  DecisionShapPanel,
} from "../components/decision";
import {
  useCanonicalDecision,
  useRanking,
  useActivePair,
  pairUniverseFromRanking,
} from "../hooks";

export function DecisionPage(): JSX.Element {
  const { pair, setPair } = useActivePair();
  const ranking = useRanking();
  const canonical = useCanonicalDecision(pair, 30);
  const universe = pairUniverseFromRanking(ranking.data);

  if (canonical.isLoading) {
    return <LoadingSpinner label={`Loading decision for ${pair}...`} />;
  }

  if (canonical.isError) {
    return (
      <ApiError
        message={canonical.error?.message}
        onRetry={() => void canonical.refetch()}
      />
    );
  }

  const data = canonical.data;

  if (!data) {
    return (
      <div className="text-center text-muted py-8">
        No decision available for {pair}
      </div>
    );
  }

  const { decision, artifact, signals, regime } = data;
  const shapValues = artifact?.shap_values ?? [];
  const expectedReturn = artifact?.expected_return ?? 0;
  const quantScore = signals?.quant_score?.value ?? 0;
  const macroScore = signals?.macro_score?.value ?? 0;
  const ragScore = signals?.rag_score?.value ?? 0;

  return (
    <section className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-2xl font-semibold text-ink">
            🎯 Decision
          </h2>
          <p className="text-sm text-muted mt-1">
            {pair} · {data.horizon_days} days · {decision?.signal_validity ?? "—"}
          </p>
        </div>

        <UniverseSelector
          currencies={universe}
          selected={pair}
          onChange={setPair}
        />
      </div>

      {/* Hero: Direction + Confidence + Actionable + Validity */}
      {decision && (
        <DecisionHero
          direction={decision.direction || "NEUTRAL"}
          confidence={decision.confidence ?? 0}
          actionable={decision.actionable ?? false}
          signalValidity={decision.signal_validity ?? "UNAVAILABLE"}
        />
      )}

      {/* Metrics: Edge + Net Return + Position Size + Expected Return */}
      {decision && (
        <DecisionMetrics
          edgeRatio={decision.edge_ratio ?? 0}
          netReturn={decision.net_return ?? 0}
          positionSize={decision.position_size ?? 0}
          expectedReturn={expectedReturn}
        />
      )}

      {/* Sizing — values from canonical backend contract */}
      {data.sizing && (
        <Panel title="📐 Position Sizing">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div>
              <div className="text-xs text-muted">Base Size</div>
              <div className="text-lg font-bold font-mono text-ink">
                {safeToFixed(data.sizing.base_size, 0)}
              </div>
            </div>

            <div>
              <div className="text-xs text-muted">Available Capacity</div>
              <div className="text-lg font-bold font-mono text-ink">
                {safeToFixed(data.sizing.available_capacity, 0)}
              </div>
            </div>

            <div>
              <div className="text-xs text-muted">Edge Multiplier</div>
              <div className="text-lg font-bold font-mono text-ink">
                {safeToFixed(data.sizing.multipliers.edge, 2)}×
              </div>
            </div>

            <div>
              <div className="text-xs text-muted">Quality Multiplier</div>
              <div className="text-lg font-bold font-mono text-ink">
                {safeToFixed(data.sizing.multipliers.quality, 2)}×
              </div>
            </div>

            <div>
              <div className="text-xs text-muted">Volatility Multiplier</div>
              <div className="text-lg font-bold font-mono text-ink">
                {safeToFixed(data.sizing.multipliers.volatility, 2)}×
              </div>
            </div>

            <div>
              <div className="text-xs text-muted">Capacity Status</div>
              <div className="text-lg font-bold text-ink">
                {data.sizing.capacity_constrained ? "Constrained" : "Available"}
              </div>
            </div>
          </div>

          {data.sizing.rejection_reason && (
            <div className="text-sm text-muted mt-4">
              Rejection reason: {data.sizing.rejection_reason}
            </div>
          )}
        </Panel>
      )}

      {/* Regime — canonical backend value */}
      <Panel title="🌐 Macro Regime">
        <div className="text-xl font-semibold text-ink">
          {regime || "UNKNOWN"}
        </div>
        <div className="text-sm text-muted mt-1">
          Current regime from the canonical decision contract.
        </div>
      </Panel>

      {/* Signals summary */}
      <Panel title="📈 Signal Scores">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <div className="text-xs text-muted">Quant Score</div>
            <div className="text-xl font-bold font-mono text-ink">
              {safeToFixed(quantScore, 4)}
            </div>
          </div>
          <div>
            <div className="text-xs text-muted">Macro Score</div>
            <div className="text-xl font-bold font-mono text-ink">
              {safeToFixed(macroScore, 4)}
            </div>
          </div>
          <div>
            <div className="text-xs text-muted">RAG Score</div>
            <div className="text-xl font-bold font-mono text-ink">
              {safeToFixed(ragScore, 4)}
            </div>
          </div>
        </div>
      </Panel>

      {/* Top SHAP drivers */}
      <Panel title="🔍 Top SHAP Drivers">
        <DecisionShapPanel shapValues={shapValues} maxItems={10} />
      </Panel>

      {/* Signal validity + rejection reason */}
      {decision && (
        <DecisionValidity
          signalValidity={decision.signal_validity ?? "UNAVAILABLE"}
          rejectionReason={decision.rejection_reason}
        />
      )}

      {/* Educational panels */}
      <ActionableInfo />
      <Panel title="📖 About the model">
        <ModelExplanation />
      </Panel>
    </section>
  );
}
