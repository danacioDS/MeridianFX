/**
 * InfoTooltip — Tooltip híbrido (hover + click + focus) sin dependencias.
 *
 * Uso:
 *   <InfoTooltip title="Policy differential">
 *     <p>Qué es: ...</p>
 *     <p>Fórmula: ...</p>
 *   </InfoTooltip>
 *
 * Comportamiento:
 *   - Desktop: aparece en hover, se cierra al salir
 *   - Móvil/touch: se abre en click, se cierra con click fuera o Escape
 *   - Accesible: focus + aria-describedby + role="tooltip"
 *
 * ⚠️  Presentational ONLY. No calcula nada.
 */
import { useEffect, useId, useRef, useState, type ReactNode } from "react";

interface InfoTooltipProps {
  title: string;
  children: ReactNode;
  /** Etiqueta opcional del trigger (default: "Más información") */
  ariaLabel?: string;
}

export function InfoTooltip({
  title,
  children,
  ariaLabel = "Más información",
}: InfoTooltipProps): JSX.Element {
  const [open, setOpen] = useState(false);
  const wrapperRef = useRef<HTMLSpanElement>(null);
  const tooltipId = useId();

  // Cerrar con Escape
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open]);

  // Cerrar al hacer click fuera
  useEffect(() => {
    if (!open) return;
    const onClick = (e: MouseEvent) => {
      if (
        wrapperRef.current &&
        !wrapperRef.current.contains(e.target as Node)
      ) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, [open]);

  return (
    <span
      ref={wrapperRef}
      className="relative inline-flex items-center"
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
    >
      <button
        type="button"
        aria-label={ariaLabel}
        aria-describedby={open ? tooltipId : undefined}
        onClick={() => setOpen((v) => !v)}
        onFocus={() => setOpen(true)}
        onBlur={(e) => {
          // No cerrar si el foco pasa al tooltip
          if (!wrapperRef.current?.contains(e.relatedTarget as Node)) {
            setOpen(false);
          }
        }}
        className="ml-1 inline-flex h-4 w-4 items-center justify-center rounded-full border border-line text-[10px] font-semibold text-muted hover:text-ink hover:border-ink focus:outline-none focus:ring-1 focus:ring-ink"
      >
        i
      </button>

      {open && (
        <span
          id={tooltipId}
          role="tooltip"
          className="absolute left-1/2 top-full z-50 mt-2 w-80 -translate-x-1/2 rounded-lg border border-line bg-paper p-3 text-left shadow-lg"
        >
          <span className="block text-xs font-semibold uppercase tracking-wider text-muted mb-2">
            {title}
          </span>
          <span className="block text-xs text-ink-soft leading-relaxed space-y-1">
            {children}
          </span>
        </span>
      )}
    </span>
  );
}
