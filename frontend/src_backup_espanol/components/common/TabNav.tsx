/**
 * Tab navigation — presentational only.
 *
 * Mockup top tab strip ("All", "Forecast", "Drivers", "Performance").
 * Active state and change handling are UI concerns only; no data logic.
 */
interface Tab {
  /** Tab identifier. */
  id: string;
  /** Tab label. */
  label: string;
}

interface TabNavProps {
  /** Ordered list of tabs. */
  tabs: Tab[];
  /** Currently active tab id. */
  activeTab: string;
  /** Tab change handler. */
  onTabChange: (id: string) => void;
}

export function TabNav({ tabs, activeTab, onTabChange }: TabNavProps): JSX.Element {
  return (
    <nav aria-label="View tabs" className="flex items-center gap-1">
      {tabs.map((tab) => {
        const isActive = tab.id === activeTab;
        return (
          <button
            key={tab.id}
            type="button"
            onClick={() => onTabChange(tab.id)}
            aria-current={isActive ? "page" : undefined}
            className={`rounded px-3 py-1.5 text-sm font-medium transition-colors ${
              isActive
                ? "bg-primary/10 text-text-primary"
                : "text-text-secondary hover:text-text-primary"
            }`}
          >
            {tab.label}
          </button>
        );
      })}
    </nav>
  );
}