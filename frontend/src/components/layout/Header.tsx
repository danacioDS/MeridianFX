import { NavLink } from 'react-router-dom';
import { useState, useEffect } from 'react';

interface HeaderProps {
  subtitle?: string;
  version?: string;
}

export function Header({ subtitle = "Financial Intelligence", version = "v2.0" }: HeaderProps): JSX.Element {
  const [liveData, setLiveData] = useState(false);
  const [time, setTime] = useState("");

  useEffect(() => {
    setLiveData(true);
    const interval = setInterval(() => {
      setTime(new Date().toLocaleTimeString());
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { to: "/", label: "Global" },
    { to: "/forecast", label: "Forecast" },
    { to: "/drivers", label: "Drivers" },
    { to: "/evaluation", label: "Evaluation" },
    { to: "/status", label: "Status" },
    { to: "/price", label: "Price" },
    { to: "/about", label: "About" },
  ];

  return (
    <header className="border-b border-line pb-4 mb-6">
      <div className="flex flex-wrap items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-serif font-bold text-ink">
              Meridian<span className="text-meridian italic">FX</span>
            </h1>
            <span className="text-xs text-muted border border-line rounded px-2 py-0.5">
              {version}
            </span>
          </div>
          <p className="text-sm text-muted">{subtitle}</p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <span className={`inline-block h-2 w-2 rounded-full ${liveData ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
            <span className="text-xs text-muted">
              {liveData ? 'Live Data' : 'Offline'}
            </span>
          </div>
          <span className="text-xs text-muted font-mono">
            {time || '--:--:--'}
          </span>
        </div>
      </div>

      <nav className="flex flex-wrap gap-1 mt-3 border-t border-line pt-3">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                isActive
                  ? 'bg-meridian text-white'
                  : 'text-muted hover:text-ink hover:bg-panel-2'
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </header>
  );
}
