import { NavLink } from "react-router-dom";

const navItems = [
  { path: "/", label: "Global" },
  { path: "/forecast", label: "Forecast" },
  { path: "/drivers", label: "Drivers" },
  { path: "/evaluation", label: "Evaluation" },
  { path: "/status", label: "Status" },
];

export function Sidebar(): JSX.Element {
  return (
    <aside className="w-48 min-h-screen border-r border-line bg-panel shrink-0 p-4 hidden md:block">
      <nav className="flex flex-col gap-1">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? "bg-meridian-soft text-meridian"
                  : "text-ink-soft hover:bg-panel-2 hover:text-ink"
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
