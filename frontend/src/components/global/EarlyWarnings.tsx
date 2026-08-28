export function EarlyWarnings(): JSX.Element {
  return (
    <div className="space-y-2 text-sm">
      <div className="flex items-start gap-3 text-ink-soft">
        <span className="text-base flex-shrink-0">⚠️</span>
        <span>Posicionamiento corto en JPY en extremo de 1 año <span className="text-muted font-mono text-xs">(z-score: -2.1)</span></span>
      </div>
      <div className="flex items-start gap-3 text-ink-soft border-t border-line pt-2">
        <span className="text-base flex-shrink-0">ℹ️</span>
        <span>Régimen risk-on confirmado (VIX &lt; 18)</span>
      </div>
    </div>
  );
}
