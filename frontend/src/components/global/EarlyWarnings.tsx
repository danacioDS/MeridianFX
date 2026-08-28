export function EarlyWarnings(): JSX.Element {
  return (
    <div className="space-y-3">
      <div className="flex items-start gap-3 text-sm text-ink-soft">
        <span className="text-base flex-shrink-0">⚠️</span>
        <div>
          <span>Posicionamiento corto en JPY en extremo de 1 año</span>
          <span className="font-mono text-xs text-muted block">z-score: -2.1</span>
        </div>
      </div>
      <div className="flex items-start gap-3 text-sm text-ink-soft border-t border-line pt-3">
        <span className="text-base flex-shrink-0">ℹ️</span>
        <div>
          <span>Régimen risk-on confirmado</span>
          <span className="font-mono text-xs text-muted block">VIX &lt; 18</span>
        </div>
      </div>
    </div>
  );
}
