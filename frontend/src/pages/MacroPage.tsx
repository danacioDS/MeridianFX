/**
 * MacroPage — Regime and macro context.
 *
 * v2.4 Sprint 5
 *
 * Consumes:
 *   GET /v1/canonical/{pair}/decision?horizon_days=30   → useCanonicalDecision
 *
 * Extracts:
 *   - data.regime                        → "UNKNOWN" | "Goldilocks" | ...
 *   - data.artifact.macro_regime         → {risk, policy, growth, inflation}
 *   - data.macro_data_status             → status, base/quote, diffs, rates
 *   - data.signals.macro_score           → { value } | null
 *
 * ⚠️  This page is PRESENTATIONAL ONLY.
 *     All analytical values come from the backend.
 * ⚠️  Handles null fields (macro_score, differentials, rates) gracefully.
 */
import {
  ApiError,
  LoadingSpinner,
  Panel,
  UniverseSelector,
} from "../components/common";
import {
  MacroHero,
  PolicyDifferentials,
  MacroMeta,
} from "../components/macro";
import {
  useActivePair,
  useCanonicalDecision,
  useRanking,
  pairUniverseFromRanking,
} from "../hooks";

export function MacroPage(): JSX.Element {
  const { pair, setPair } = useActivePair();
  const ranking = useRanking();
  const universe = pairUniverseFromRanking(ranking.data);
  const decision = useCanonicalDecision(pair, 30);

  if (decision.isLoading) {
    return <LoadingSpinner label={`Loading macro context for ${pair}...`} />;
  }

  if (decision.isError) {
    return (
      <ApiError
        message={decision.error?.message}
        onRetry={() => void decision.refetch()}
      />
    );
  }

  const data = decision.data;

  if (!data) {
    return (
      <div className="text-center text-muted py-8">
        No macro data available for {pair}
      </div>
    );
  }

  const macroRegime = data.artifact?.macro_regime ?? null;
  const macroStatus = data.macro_data_status;
  const macroScore = data.signals?.macro_score?.value ?? null;

  return (
    <section className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-2xl font-semibold text-ink">
            🌐 Macro
          </h2>
          <p className="text-sm text-muted mt-1">
            {pair} · Regime, policy, growth, inflation
          </p>
        </div>

        <UniverseSelector
          currencies={universe}
          selected={pair}
          onChange={setPair}
        />
      </div>

      {/* Hero: regime + macro_regime + status + macro_score */}
      <MacroHero
        regime={data.regime ?? "UNKNOWN"}
        macroRegime={macroRegime}
        macroStatus={macroStatus?.status ?? "—"}
        macroScore={macroScore}
      />

      {/* Differentials + rates */}
      <Panel title="📊 Policy & Differentials">
        <PolicyDifferentials
          base={macroStatus?.base ?? "—"}
          quote={macroStatus?.quote ?? "—"}
          policyDifferential={macroStatus?.policy_differential ?? null}
          growthDifferential={macroStatus?.growth_differential ?? null}
          inflationDifferential={macroStatus?.inflation_differential ?? null}
          baseRate={macroStatus?.base_rate ?? null}
          quoteRate={macroStatus?.quote_rate ?? null}
        />
      </Panel>

      {/* Data availability */}
      <Panel title="📡 Data Availability">
        <MacroMeta
          base={macroStatus?.base ?? "—"}
          quote={macroStatus?.quote ?? "—"}
          baseAvailable={macroStatus?.base_available ?? false}
          quoteAvailable={macroStatus?.quote_available ?? false}
          reason={macroStatus?.reason ?? null}
        />
      </Panel>
    </section>
  );
}
