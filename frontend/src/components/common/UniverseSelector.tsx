interface UniverseSelectorProps {
  currencies: string[];
  selected: string;
  onChange: (pair: string) => void;
}

export function UniverseSelector({
  currencies,
  selected,
  onChange,
}: UniverseSelectorProps): JSX.Element {
  // Si no hay monedas, mostrar placeholder
  const displayCurrencies = currencies.length > 0 ? currencies : ["USD/JPY"];

  return (
    <div className="flex items-center gap-3 flex-wrap border border-line rounded-mockup px-4 py-2 bg-paper">
      <span className="text-[10px] text-muted uppercase tracking-wider">
        Universe
      </span>
      <div className="flex gap-1.5 flex-wrap">
        {displayCurrencies.map((pair) => {
          const isActive = pair === selected;
          return (
            <button
              key={pair}
              onClick={() => onChange(pair)}
              className={`font-mono text-xs font-semibold px-2.5 py-1 rounded-md transition-colors ${
                isActive
                  ? "bg-meridian-soft text-meridian border border-meridian"
                  : "text-ink-soft hover:bg-panel-2"
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
