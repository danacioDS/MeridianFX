/**
 * MacroPage — Regime and macro context.
 *
 * ⚠️ PLACEHOLDER — to be implemented in Sprint 5.
 */
import {
  Panel,
  UniverseSelector,
} from "../components/common";
import {
  useActivePair,
  useRanking,
  pairUniverseFromRanking,
} from "../hooks";

export function MacroPage(): JSX.Element {
  const { pair, setPair } = useActivePair();
  const ranking = useRanking();
  const universe = pairUniverseFromRanking(ranking.data);

  return (
    <section className="flex flex-col gap-6">
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

      <Panel title="Coming soon">
        <p className="text-sm text-muted">
          Macro regime, policy/growth/inflation differentials, and
          economic filter will be integrated here in Sprint 5.
        </p>
      </Panel>
    </section>
  );
}
