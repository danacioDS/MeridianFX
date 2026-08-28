import { useState } from 'react';

interface UniverseSelectorProps {
  currencies: string[];
  selected: string;
  onChange: (pair: string) => void;
}

export function UniverseSelector({ currencies, selected, onChange }: UniverseSelectorProps): JSX.Element {
  const [isOpen, setIsOpen] = useState(false);

  if (!currencies || currencies.length === 0) {
    return <div className="text-sm text-muted">No currencies available</div>;
  }

  return (
    <div className="border border-line rounded-xl px-4 py-2.5 flex items-center gap-4 flex-wrap bg-paper">
      <span className="text-[10px] uppercase tracking-wider text-muted font-semibold">Currency Universe</span>
      
      {/* Chips de monedas estilo mockup */}
      <div className="flex gap-1.5 flex-wrap">
        <span className="font-mono text-[11.5px] font-semibold px-3 py-1 rounded-lg border border-navy bg-navy text-white cursor-default">
          USD
        </span>
        {currencies.map((curr) => {
          const pair = `USD/${curr}`;
          const isActive = pair === selected;
          return (
            <button
              key={curr}
              onClick={() => onChange(pair)}
              className={`font-mono text-[11.5px] font-semibold px-3 py-1 rounded-lg border transition-all ${
                isActive
                  ? 'bg-meridian-soft border-meridian text-meridian'
                  : 'bg-paper border-line text-ink-soft hover:bg-meridian-soft hover:border-meridian hover:text-meridian'
              }`}
            >
              {curr}
            </button>
          );
        })}
      </div>

      <span className="text-[11px] text-muted ml-auto hidden sm:inline">
        {currencies.length} monedas · {currencies.length} pares
      </span>
    </div>
  );
}
