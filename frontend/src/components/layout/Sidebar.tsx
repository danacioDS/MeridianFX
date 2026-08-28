/**
 * Sidebar navigation.
 *
 * Items: Global, Forecast, Drivers, Evaluation, Status. Active route
 * highlighting via NavLink. Collapses to a compact rail under 768px.
 */
import { NavLink } from "react-router-dom";

const NAV_ITEMS: ReadonlyArray<{ to: string; label: string; end?: boolean }> = [
  { to: "/", label: "Global", end: true },
  { to: "/forecast", label: "Forecast" },
  { to: "/drivers", label: "Drivers" },
  { to: "/evaluation", label: "Evaluation" },
  { to: "/status", label: "Status" },
];

export function Sidebar(): JSX.Element {
  return (
    <aside className="flex w-56 shrink-0 flex-col gap-6 border-r border-border bg-surface p-4 md:w-64">
      <div className="flex items-center gap-2 px-2">
        <span
          aria-hidden="true"
          className="h-3 w-3 rounded-full bg-primary"
        />
        <span className="text-sm font-bold tracking-wide text-text-primary">MERIDIAN FX</span>
      </div>

      <nav aria-label="Main navigation" className="flex flex-col gap-1">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) =>
              [
                "rounded px-3 py-2 text-sm transition-colors",
                isActive
                  ? "bg-background font-semibold text-primary"
                  : "text-text-secondary hover:bg-background hover:text-text-primary",
              ].join(" ")
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}