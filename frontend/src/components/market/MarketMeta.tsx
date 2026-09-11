import { formatDateTime } from "../../utils";

interface MarketMetaProps {
  asOf: string | null | undefined;
  lastDate: string | null | undefined;
  source: string | null | undefined;
  freshness: string | null | undefined;
  volatility?: number | null | undefined;
}

export function MarketMeta({
  asOf,
  lastDate,
  source,
  freshness,
  volatility,
}: MarketMetaProps): JSX.Element {
  return (
    <div className="p-4 bg-panel-2 rounded-lg border border-line">
      <div className="text-xs uppercase tracking-wide text-muted mb-3">
        Data metadata
      </div>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <div>
          <div className="text-xs text-muted">As of</div>
          <div className="text-sm text-ink">
            {formatDateTime(asOf)}
          </div>
        </div>

        <div>
          <div className="text-xs text-muted">
            Last market date
          </div>
          <div className="text-sm text-ink">
            {lastDate || "N/A"}
          </div>
        </div>

        <div>
          <div className="text-xs text-muted">Source</div>
          <div className="text-sm text-ink">
            {source || "N/A"}
          </div>
        </div>

        <div>
          <div className="text-xs text-muted">Freshness</div>
          <div className="text-sm text-ink">
            {freshness || "N/A"}
          </div>
        </div>

        <div>
          <div className="text-xs text-muted">Volatility</div>
          <div className="text-sm text-ink">
            {volatility != null ? `${volatility.toFixed(2)}%` : "N/A"}
          </div>
        </div>
      </div>
    </div>
  );
}
