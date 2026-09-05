import React from 'react';
import { FX_MARKET_CONVENTION } from '../../constants/fxPairs';

export function MarketConvention() {
  return (
    <div className="text-xs text-muted bg-panel/50 rounded-lg p-3 border border-line/50">
      <div className="flex items-center gap-2">
        <span className="font-medium text-ink">ⓘ {FX_MARKET_CONVENTION.title}</span>
      </div>
      <p className="mt-1 text-[11px] leading-relaxed">
        {FX_MARKET_CONVENTION.text}
      </p>
      <div className="mt-2 flex flex-wrap gap-3 text-[10px] font-mono text-muted">
        <span>EUR/USD → 1 EUR = X USD</span>
        <span>GBP/USD → 1 GBP = X USD</span>
        <span>USD/JPY → 1 USD = X JPY</span>
        <span>USD/BOB → 1 USD = X BOB</span>
      </div>
    </div>
  );
}
