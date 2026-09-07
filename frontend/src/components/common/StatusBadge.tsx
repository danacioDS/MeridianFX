interface StatusBadgeProps {
  status: string;
  label?: string;
}

export function StatusBadge({ status, label }: StatusBadgeProps) {
  const colors: Record<string, string> = {
    FULL: 'bg-green-100 text-green-800',
    PARTIAL: 'bg-yellow-100 text-yellow-800',
    UNAVAILABLE: 'bg-gray-100 text-gray-500',
    UNKNOWN: 'bg-gray-100 text-gray-500',
    STALE: 'bg-orange-100 text-orange-800',
    AVAILABLE: 'bg-green-100 text-green-800',
  };

  const labels: Record<string, string> = {
    FULL: '✅ Disponible',
    PARTIAL: '⚠️ Parcial',
    UNAVAILABLE: '❌ No disponible',
    UNKNOWN: '❓ Desconocido',
    STALE: '🔄 Desactualizado',
    AVAILABLE: '✅ Disponible',
  };

  const color = colors[status] || 'bg-gray-100 text-gray-500';
  const displayLabel = label || labels[status] || status;

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${color}`}>
      {displayLabel}
    </span>
  );
}
