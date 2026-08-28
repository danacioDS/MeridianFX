import { Link, useLocation } from 'react-router-dom';

const tabs = [
  { path: '/', label: 'Global' },
  { path: '/forecast', label: 'Forecast' },
  { path: '/drivers', label: 'Drivers' },
  { path: '/evaluation', label: 'Evaluation' },
  { path: '/status', label: 'Status' },
];

export function Header(): JSX.Element {
  const location = useLocation();

  return (
    <div className="w-full">
      {/* Top Bar - estilo mockup con FX verde */}
      <div className="flex items-end justify-between pb-4 border-b-2 border-ink mb-4 flex-wrap gap-3">
        <div className="flex items-baseline gap-3">
          <span className="w-3 h-3 rounded-full bg-meridian inline-block -translate-y-0.5"></span>
          <span className="font-serif text-4xl tracking-wide">
            Meridian<span className="italic text-meridian font-normal">FX</span>
          </span>
          <span className="text-xs uppercase tracking-widest text-muted ml-1">Financial Intelligence</span>
          <span className="text-[11px] font-mono text-meridian bg-meridian-soft px-2.5 py-0.5 rounded-full ml-1">v2.0</span>
        </div>
        <div className="text-right text-sm text-ink-soft">
          <div className="text-base font-medium">{new Date().toLocaleDateString('es-ES', { year: 'numeric', month: 'long', day: 'numeric' })}</div>
          <div className="flex gap-4 justify-end items-center mt-1 flex-wrap text-sm">
            <span className="text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded flex items-center gap-1.5 whitespace-nowrap bg-bull-soft text-bull">
              <span className="w-1.5 h-1.5 rounded-full bg-bull inline-block"></span>
              Live Data
            </span>
            <span><span className="w-1.5 h-1.5 rounded-full bg-bull inline-block mr-1.5"></span>Fresh · {new Date().toLocaleTimeString()}</span>
            <span className="font-mono text-sm font-semibold text-ink">9 modelos activos</span>
          </div>
        </div>
      </div>

      {/* Tab Navigation - más grandes */}
      <div className="flex gap-8 border-b border-line mb-5 overflow-x-auto">
        {tabs.map((tab) => {
          const isActive = location.pathname === tab.path || (tab.path === '/' && location.pathname === '/');
          return (
            <Link
              key={tab.path}
              to={tab.path}
              className={`text-base font-semibold py-3 border-b-2 cursor-pointer whitespace-nowrap transition-all ${
                isActive 
                  ? 'text-ink border-meridian' 
                  : 'text-muted border-transparent hover:text-ink'
              }`}
            >
              {tab.label}
            </Link>
          );
        })}
      </div>
    </div>
  );
}
