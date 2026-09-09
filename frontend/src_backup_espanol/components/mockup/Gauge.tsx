/**
 * Gauge visual - Probabilidad calibrada
 * Diseño del mockup + datos reales
 */
interface GaugeProps {
  probability: number;  // 0-1
  label?: string;
  size?: 'small' | 'medium' | 'large';
}

export function Gauge({ probability, label = 'Probabilidad', size = 'large' }: GaugeProps) {
  const percent = Math.round(probability * 100);
  const isBullish = probability > 0.5;
  const color = isBullish ? '#0E8F5F' : '#C4453A';
  
  const sizes = {
    small: { width: 120, height: 60, fontSize: 24 },
    medium: { width: 200, height: 80, fontSize: 36 },
    large: { width: 280, height: 100, fontSize: 48 }
  };
  
  const { width, height } = sizes[size];
  const centerX = width / 2;
  const centerY = height - 10;
  const radius = Math.min(width, height * 2) * 0.38;
  
  // Ángulos: -120° a +120° (de bajista a alcista)
  const startAngle = -120;
  const endAngle = 120;
  const angleRange = endAngle - startAngle;
  const angle = startAngle + (probability * angleRange);
  
  // Convertir a radianes
  const angleRad = (angle * Math.PI) / 180;
  const endX = centerX + radius * Math.sin(angleRad);
  const endY = centerY - radius * Math.cos(angleRad);
  
  return (
    <div className="flex flex-col items-center">
      <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
        {/* Arco de fondo (gradiente) */}
        <path
          d={`M ${centerX - radius * 0.87} ${centerY - radius * 0.5} 
              A ${radius} ${radius} 0 0 1 ${centerX + radius * 0.87} ${centerY - radius * 0.5}`}
          fill="none"
          stroke="#E6E9EE"
          strokeWidth="8"
          strokeLinecap="round"
        />
        
        {/* Arco de probabilidad (color dinámico) */}
        <path
          d={`M ${centerX - radius * 0.87} ${centerY - radius * 0.5} 
              A ${radius} ${radius} 0 0 1 ${endX} ${endY}`}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
        />
        
        {/* Marcador */}
        <circle
          cx={endX}
          cy={endY}
          r="8"
          fill="white"
          stroke={color}
          strokeWidth="3"
        />
        
        {/* Etiquetas de extremos */}
        <text x="10" y={height - 5} fontSize="10" fill="#8891A0" fontFamily="IBM Plex Mono">
          Bajista
        </text>
        <text x={width - 55} y={height - 5} fontSize="10" fill="#8891A0" fontFamily="IBM Plex Mono">
          Alcista
        </text>
      </svg>
      
      {/* Valor */}
      <div className="mt-1 text-center">
        <div className="font-serif text-4xl font-bold" style={{ color }}>
          {percent}%
        </div>
        <div className="text-xs text-muted uppercase tracking-wider">{label}</div>
      </div>
    </div>
  );
}
