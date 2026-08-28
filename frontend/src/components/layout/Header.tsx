import { useStatus } from "../../hooks";
import { getStatusColor, getStatusLabel, formatDateTime } from "../../utils";

export function Header(): JSX.Element {
  const { data } = useStatus();

  const systemStatus = data?.system_status ?? "UNKNOWN";
  const statusColor = getStatusColor(systemStatus);
  const statusLabel = getStatusLabel(systemStatus);
  const timestamp = data?.timestamp ? formatDateTime(data.timestamp) : "—";

  return (
    <header className="border-b border-line bg-panel px-6 py-4">
      <div className="flex items-center justify-between max-w-7xl mx-auto">
        {/* Marca + Organización */}
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-meridian inline-block" />
          <span className="font-serif text-xl text-ink">
            Meridian<span className="italic text-meridian">FX</span>
          </span>
          <span className="text-[10px] text-muted uppercase tracking-widest ml-1 hidden sm:inline">
            Financial Intelligence
          </span>
          <span className="text-[9px] font-mono text-meridian bg-meridian-soft px-2 py-0.5 rounded-full">
            Stratus Intelligence
          </span>
        </div>

        {/* Estado del sistema */}
        <div className="flex items-center gap-6 text-sm">
          <div className="flex items-center gap-2">
            <span
              className="w-2 h-2 rounded-full inline-block"
              style={{ backgroundColor: statusColor }}
            />
            <span className="text-ink-soft">{statusLabel}</span>
          </div>
          <span className="text-xs text-muted font-mono">{timestamp}</span>
        </div>
      </div>
    </header>
  );
}
