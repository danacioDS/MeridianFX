import React from 'react';
import { FX_PAIRS, FX_PAIR_LABELS, FX_MARKET_CONVENTION } from '../../constants/fxPairs';

interface UniverseSelectorProps {
  selected: string;
  onChange: (pair: string) => void;
  showConvention?: boolean;
}

export function UniverseSelector({ selected, onChange, showConvention = true }: UniverseSelectorProps) {
  return (
    <div className="border border-line rounded-xl px-4 py-2.5 flex items-center gap-4 flex-wrap bg-paper">
      <span className="text-[10px] uppercase tracking-wider text-muted font-semibold">
        Currency Universe
      </span>
      
      <div className="flex gap-1.5 flex-wrap">
        <span className="font-mono text-[11.5px] font-semibold px-3 py-1 rounded-lg border border-navy bg-navy text-white cursor-default">
          USD
        </span>
        
        {FX_PAIRS.map((pair) => {
          const isActive = pair === selected;
          
          return (
            <button
              key={pair}
              onClick={() => onChange(pair)}
              className={`font-mono text-[11.5px] font-medium px-3 py-1 rounded-lg border transition-colors ${
                isActive
                  ? 'bg-primary/10 border-primary text-primary'
                  : 'border-line hover:border-primary/30 text-muted hover:text-ink'
              }`}
            >
              {pair}
            </button>
          );
        })}
      </div>
      
      <span className="text-[11px] text-muted ml-auto hidden sm:inline">
        {FX_PAIRS.length} monedas · {FX_PAIRS.length} pares
      </span>
      
      {showConvention && (
        <div className="text-[10px] text-muted ml-2 hidden lg:block" title={FX_MARKET_CONVENTION.text}>
          ⓘ {FX_MARKET_CONVENTION.title}
        </div>
      )}
    </div>
  );
}
