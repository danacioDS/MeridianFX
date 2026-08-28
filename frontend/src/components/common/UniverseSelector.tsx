/**
 * Universe selector — presentational only.
 *
 * Renders a pair selector. The currency universe is supplied by the parent
 * (composition) from RankingResponse.opportunities[].pair — never hard-coded
 * or inferred here. Selection state and change handling are UI concerns only.
 */
interface UniverseSelectorProps {
  /** Available currency pairs. */
  currencies: string[];
  /** Currently selected pair. */
  selected: string;
  /** Selection change handler (UI only). */
  onChange: (pair: string) => void;
}

export function UniverseSelector({
  currencies,
  selected,
  onChange,
}: UniverseSelectorProps): JSX.Element {
  return (
    <div className="flex items-center gap-3" role="group" aria-label="Currency universe">
      <span className="text-xs text-text-secondary">Universe</span>
      <div className="flex flex-wrap gap-1.5">
        {currencies.map((pair) => {
          const isActive = pair === selected;
          return (
            <button
              key={pair}
              type="button"
              onClick={() => onChange(pair)}
              aria-pressed={isActive}
              className={`rounded border px-2.5 py-1 text-xs font-medium transition-colors ${
                isActive
                  ? "border-primary bg-primary/10 text-text-primary"
                  : "border-border bg-background text-text-secondary hover:border-primary"
              }`}
            >
              {pair}
            </button>
          );
        })}
      </div>
    </div>
  );
}