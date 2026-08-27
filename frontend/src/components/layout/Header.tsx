/**
 * Header (composition layer).
 *
 * Thin composition wrapper around the presentational common/Header. Owns the
 * data access (useStatus, useLocation) and the refresh control; passes view
 * values down via props. Presentational rendering lives in common/Header.
 */
import { useLocation } from "react-router-dom";
import { useStatus } from "../../hooks";
import { Header as PresentationalHeader } from "../common/Header";

const PAGE_TITLES: Record<string, string> = {
  "/": "Global Intelligence",
  "/forecast": "Forecast Dashboard",
  "/drivers": "Drivers & Explanation",
  "/evaluation": "Evaluation & Performance",
  "/status": "System Status",
};

export function Header(): JSX.Element {
  const { pathname } = useLocation();
  const status = useStatus();
  const title = PAGE_TITLES[pathname] ?? "Meridian FX";

  return (
    <PresentationalHeader
      title={title}
      status={status.data?.system_status ?? null}
      timestamp={status.data?.timestamp ?? null}
      dataQuality={status.data?.intelligence.data_quality.status ?? null}
    >
      <button
        type="button"
        onClick={() => void status.refetch()}
        disabled={status.isFetching}
        className="rounded border border-border bg-background px-3 py-1.5 text-sm text-text-primary transition-colors hover:border-primary disabled:cursor-not-allowed disabled:opacity-50"
      >
        Refresh
      </button>
    </PresentationalHeader>
  );
}