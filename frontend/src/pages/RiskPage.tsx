/**
 * RiskPage — Canonical Risk Assessment (v2.3).
 *
 * Consumes: GET /v1/canonical/{pair}/risk?horizon_days={h}
 *
 * ⚠️  This page is PRESENTATIONAL ONLY.
 *     It does NOT compute risk_score, risk_level, or contributions.
 *     All analytical values come from the backend (RiskEngine v2.3.0).
 */
import {
  ApiError,
  LoadingSpinner,
  EmptyState,
  Panel,
  UniverseSelector,
} from "../components/common";
import { RiskScoreCard, RiskDriversPanel } from "../components/risk";
import {
  useActivePair,
  useCanonicalRisk,
  useRanking,
  pairUniverseFromRanking,
} from "../hooks";

export function RiskPage(): JSX.Element {
  const { pair, setPair } = useActivePair();
  const ranking = useRanking();
  const universe = pairUniverseFromRanking(ranking.data);
  const risk = useCanonicalRisk(pair, 30);

  if (risk.isLoading) {
    return <LoadingSpinner label={`Loading risk assessment for ${pair}...`} />;
  }

  if (risk.isError) {
    return (
      <ApiError
        message={risk.error?.message}
        onRetry={() => void risk.refetch()}
      />
    );
  }

  const data = risk.data;

  if (!data) {
    return (
      <EmptyState
        title="No risk assessment available"
        message={pair}
      />
    );
  }

  // Guard: risk can be null when the model is unavailable for this pair
  if (!data.risk) {
    return (
      <section className="flex flex-col gap-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-2xl font-semibold text-ink">
              ⚠️ Risk Assessment
            </h2>
            <p className="text-sm text-muted mt-1">
              {pair} · {data.horizon_days} days · UNAVAILABLE
            </p>
          </div>

          <UniverseSelector
            currencies={universe}
            selected={pair}
            onChange={setPair}
          />
        </div>

        <Panel title="Risk Assessment Unavailable">
          <p className="text-sm text-muted">
            No risk assessment is available for {pair}. This typically
            occurs when the underlying model is not trained for this
            currency pair.
          </p>
          {data.decision_summary && (
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
              <div>
                <div className="text-xs text-muted">Signal validity</div>
                <div className="font-semibold text-ink">
                  {data.decision_summary?.signal_validity ?? "—"}
                </div>
              </div>
              <div>
                <div className="text-xs text-muted">Macro status</div>
                <div className="font-semibold text-ink">
                  {data.macro_data_status?.status ?? "—"}
                </div>
              </div>
            </div>
          )}
        </Panel>
      </section>
    );
  }

  const { risk: assessment, macro_data_status, decision_summary } = data;
  const macroStatus = macro_data_status?.status ?? "—";
  const actionable = decision_summary?.actionable;
  const validity = decision_summary?.signal_validity ?? "—";

  return (
    <section className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-2xl font-semibold text-ink">
            ⚠️  Risk Assessment
          </h2>
          <p className="text-sm text-muted mt-1">
            {pair} · {data.horizon_days} days · {macroStatus}
          </p>
        </div>

        <UniverseSelector
          currencies={universe}
          selected={pair}
          onChange={setPair}
        />
      </div>

      {/* Risk Score */}
      <RiskScoreCard
        score={assessment.risk_score}
        level={assessment.risk_level}
        methodologyVersion={assessment.methodology_version}
      />

      {/* Context summary */}
      <Panel title="📋 Context">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <div className="text-xs text-muted">Macro status</div>
            <div className="font-semibold text-ink">{macroStatus}</div>
          </div>
          <div>
            <div className="text-xs text-muted">Signal actionable</div>
            <div className="font-semibold text-ink">
              {actionable === true ? "YES" : actionable === false ? "NO" : "—"}
            </div>
          </div>
          <div>
            <div className="text-xs text-muted">Signal validity</div>
            <div className="font-semibold text-ink">{validity}</div>
          </div>
        </div>
      </Panel>

      {/* Risk Drivers */}
      <Panel title="🔍 Risk Drivers">
        <RiskDriversPanel drivers={assessment.drivers} />
      </Panel>
    </section>
  );
}
