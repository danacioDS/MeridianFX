export function DataTimestamps(): JSX.Element {
  return (
    <div className="grid grid-cols-2 gap-2 text-sm">
      <div className="flex justify-between py-1.5 border-b border-line last:border-b-0">
        <span className="text-muted">Forecast horizon</span>
        <b className="font-mono text-ink">5D</b>
      </div>
      <div className="flex justify-between py-1.5 border-b border-line last:border-b-0">
        <span className="text-muted">Market data</span>
        <b className="font-mono text-ink">08:00 UTC</b>
      </div>
      <div className="flex justify-between py-1.5 border-b border-line last:border-b-0">
        <span className="text-muted">Macro data</span>
        <b className="font-mono text-ink">Latest available</b>
      </div>
      <div className="flex justify-between py-1.5 border-b border-line last:border-b-0">
        <span className="text-muted">Policy assessment</span>
        <b className="font-mono text-ink">2026-08-25</b>
      </div>
    </div>
  );
}
