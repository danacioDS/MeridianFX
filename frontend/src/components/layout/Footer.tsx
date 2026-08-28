export function Footer(): JSX.Element {
  return (
    <footer className="border-t border-line bg-panel px-6 py-4 mt-6">
      <div className="flex flex-col items-center justify-between gap-2 max-w-7xl mx-auto text-xs text-muted sm:flex-row">
        <span>
          Meridian FX © 2026 ·{' '}
          <span className="font-medium text-ink-soft">Stratus Intelligence</span>
        </span>
        <span>
          Developed by{' '}
          <span className="font-medium text-ink-soft">Daniel Canedo, MSc in Economics</span>
        </span>
      </div>
    </footer>
  );
}
