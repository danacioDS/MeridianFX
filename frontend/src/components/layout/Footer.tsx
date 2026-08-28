/**
 * Footer — Presentacional
 * 
 * Mismo footer en todas las páginas
 */
export function Footer(): JSX.Element {
  return (
    <footer className="w-full border-t border-line mt-8 pt-4">
      <div className="text-center">
        <p className="text-sm text-ink-soft">
          <strong>Stratus Intelligence</strong> · MeridianFX · © {new Date().getFullYear()} | MSc. Daniel Canedo
        </p>
        <p className="text-xs text-muted mt-1">
          4-Layer Architecture: Data → Research → Decision → Intelligence
        </p>
      </div>
    </footer>
  );
}
